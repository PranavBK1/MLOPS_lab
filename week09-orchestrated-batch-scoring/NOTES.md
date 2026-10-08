# NOTES.md — Week 9: Orchestrated Batch Scoring

**Student ID used with `generate_for_student.py`:**
`142602014` (derived seed: `1215849417`)


## notify retry count

`notify` took **3 attempts** in my run (`dag_run_summary.json` →
`"notify": {"status": "success", "attempts": 3}`). Attempts 1 and 2 raised
the simulated `RuntimeError`, and attempt 3 succeeded. The task was configured with
`max_retries=3` (up to 4 attempts total), so it succeeded with one retry
left. Every other task (`extract`, `score`, `load`) succeeded on its first
attempt. The whole DAG ended green, and `batch_report.json` covers all 40
images (153 detections).


## Branch independence

`load` succeeds because it **does not depend on `notify`**. Both tasks depend
only on `score`. Once `score` has written `per_image_counts` and
`total_detections` into the shared context, `load` already has everything it
needs. Nothing `notify` does or fails to do changes those inputs.

In my run the topological order was `extract → score → load → notify`, so
`load` had actually finished before `notify` made its first attempt. Even
with the other valid order (`notify` before `load`), `load` would still
succeed. `notify` failing transiently is handled *inside*
`run_task_with_retry`, so it never becomes a DAG-level failure. The
orchestrator only stops the run if a task is still failing after all its
retries.

What this says about DAG design:

- **A failure should only block the tasks that need its output.** Edges in a
  DAG represent data or ordering dependencies. If there is no path from
  `notify` to `load`, a failure in `notify` has no reason to stop `load`.
  Airflow follows the same idea: a failed task marks its *downstream* tasks
  `upstream_failed` and leaves sibling branches alone.
- **My `run_dag` is stricter than that, as the spec asks.** It stops at the
  first unrecoverable failure in the *linear* topological order. That means a
  permanently failing `notify` placed before `load` in the order would also
  skip `load`, even though `load` doesn't depend on it. That is safe, but it
  costs availability. A production orchestrator would skip only the
  *descendants* of the failed node, so the batch report still gets written
  when the alerting webhook is down.
- **Put side effects that matter for correctness on the critical path, and
  keep best-effort ones off it.** Writing the report is the actual
  deliverable. Sending a notification is best-effort. Making them siblings,
  rather than chaining `score → notify → load`, keeps an unreliable external
  service from blocking the core output.


## Retry cost under FinOps

The current strategy retries every failure the same way: a fixed
`max_retries` with a fixed 0.1 s delay. That is fine when a retry costs
nothing. If `notify` were a **metered API billed per attempt**, every failed
attempt would be paid for. This run used 3 billed calls to get 1 useful
notification, so 2/3 of the spend was waste.

What I would change:

1. **Retry only errors that can succeed on a retry.** Retry timeouts,
   HTTP 429 and 5xx. Fail immediately, without retrying, on 4xx client errors
   such as a bad payload, an expired auth token or a quota already exceeded.
   Those will fail the same way every time, and each retry is money spent
   for nothing.
2. **Exponential backoff with jitter, plus honoring `Retry-After`.** A fixed
   0.1 s delay calls the provider again while it is still unhealthy, which
   pays for attempts that are almost certain to fail and can make an outage
   worse. Waiting longer between attempts raises the chance that each paid
   attempt succeeds.
3. **Set a retry budget based on value, not a constant.** Choose
   `max_retries` per task from *cost per attempt × attempts* against the
   value of success. A best-effort notification might get 1 retry. A
   critical, idempotent task that is cheap to call might get more. Add a
   per-run or per-day spend cap (or a circuit breaker) so a provider outage
   can't turn into a large bill.
4. **Idempotency keys.** If an attempt actually went through but the
   response was lost, a retry could be billed (and delivered) twice. An
   idempotency key lets the provider deduplicate it.
5. **Batch, or degrade gracefully.** Send one notification per batch, not per
   image. When the budget runs out, record the alert in a cheap queue or log
   to send later, and don't fail the DAG over it.

**Why "retry every failed task the same way" is a risky default:** tasks
differ in what a retry costs (free local compute vs. a paid API vs. a GPU
job), in whether retrying can help (transient vs. permanent errors), and
in what failure means (a critical report vs. a best-effort ping). A single
policy ends up wrong in at least one of these cases. It is too timid for
cheap critical tasks, and for expensive ones it is too aggressive. Without
anyone noticing, it also multiplies spend during exactly the incidents
where the calls are least likely to succeed. Retry count becomes a cost
multiplier hidden in config, so FinOps practice says to set it per task,
make it visible, and cap it.
