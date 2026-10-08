# Week 9 — Orchestrated Batch Scoring

**DS5619 Machine Learning Systems Operations · Track B (BMD-45 vehicle detection)**

This project batch-scores vehicle-detection images with a small,
self-contained **DAG orchestrator**. It shows the two main ideas behind
tools like Airflow without the scheduler, webserver and metadata database:

1. A pipeline is a **dependency graph**, run in *topological order* rather
   than top to bottom.
2. Each task gets its own **retries**, so a transient failure doesn't fail
   the whole run.

## The DAG

```
extract --> score --> load
                  \-> notify
```

| Task | Depends on | What it does |
|---|---|---|
| `extract` | — | Lists every `*.jpg` under `data/fixtures/` |
| `score` | `extract` | Runs the mock detector on each image and accumulates detection counts |
| `load` | `score` | Writes `batch_report.json` |
| `notify` | `score` | Stand-in for a flaky webhook: fails twice, then succeeds (`max_retries=3`) |

## Result

```
Execution order: ['extract', 'score', 'load', 'notify']
  extract: {'status': 'success', 'attempts': 1}
  score:   {'status': 'success', 'attempts': 1}
  load:    {'status': 'success', 'attempts': 1}
  notify:  {'status': 'success', 'attempts': 3}
```

| | camera_A_daylight | camera_B_lowlight | Total |
|---|---|---|---|
| images scored | 20 | 20 | **40** |
| detections | 75 | 78 | **153** |

`notify` failed on attempts 1 and 2 and succeeded on attempt 3. Because of
the per-task retries, the whole DAG still finished green. See
[NOTES.md](NOTES.md) for why `load` doesn't care about its sibling's
failures and how the retry strategy should change once each attempt costs
money (FinOps).

## What was done

1. **Generated personalized data:** ran
   `python generate_for_student.py --student-id 142602014`. It writes
   20 synthetic images per camera (40 total) plus `_annotations.coco.json`
   (157 ground-truth boxes) into `data/fixtures/`, seeded deterministically
   from the student ID (seed `1215849417`).
2. **Implemented the three `# TODO` functions in
   [`src/mini_orchestrator.py`](src/mini_orchestrator.py):**
   - **`topological_order(tasks)`** uses Kahn's algorithm. It first checks
     that every `depends_on` entry names a task that exists, and raises
     `ValueError` if one doesn't. It then computes each task's in-degree,
     repeatedly takes a task with zero unmet dependencies, and lowers the
     in-degree of the tasks that depend on it. If any tasks are left over,
     they form a cycle, which also raises `ValueError` (self-loops included).
     Duplicate entries in `depends_on` are de-duplicated, and the order is
     deterministic for a given task definition.
   - **`run_task_with_retry(task, context)`** makes up to
     `max_retries + 1` attempts and sleeps `retry_delay_seconds` between
     them. It returns the number of the attempt that succeeded (1 on the
     first try). If every attempt fails, it re-raises the **last** exception
     unchanged with a bare `raise`.
   - **`run_dag(tasks, context)`** computes the order, then runs each task
     through `run_task_with_retry` with the **same shared `context` dict**,
     so downstream tasks can read what upstream tasks wrote. It records
     `{"status": "success", "attempts": N}` for each task. On an
     unrecoverable failure it records
     `{"status": "failed", "attempts": N, "error": str(exc)}` and **stops**,
     so no later task runs. To report `N` for a failed task, it wraps the
     task's function in a small counter, without changing the caller's
     `Task` objects.
3. **Ran the pipeline** with `python src/run_pipeline.py`. It wrote
   `batch_report.json` (per-image detection counts) and
   `dag_run_summary.json` (execution order and per-task status/attempts).
4. **Verified:**
   - All **10/10** self-check tests in `tests/test_smoke.py` pass.
   - Extra checks beyond the provided tests:
     - a diamond DAG (`a → b, a → c, b+c → d`) orders correctly
     - a self-loop and a two-node cycle both raise `ValueError`
     - a task that always fails with `max_retries=2` reports
       `attempts: 3`, and the run stops before its dependents run
5. **Wrote [NOTES.md](NOTES.md):** it records the student ID, the
   `notify` attempt count, why sibling branches are independent, and a
   cost-aware retry strategy (retry only retryable errors, exponential
   backoff with jitter, per-task retry budgets and spend caps, idempotency
   keys).

`src/run_pipeline.py`, `src/mock_detector.py` and `data/fixtures/` were not
edited by hand, as the assignment requires.

## How to run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1. Regenerate the personalized fixtures (already committed)
python generate_for_student.py --student-id 142602014

# 2. Run the DAG -> batch_report.json + dag_run_summary.json
python src/run_pipeline.py

# 3. Self-check
pytest tests/ -q
```

## Project structure

```
week09-orchestrated-batch-scoring/
├── src/
│   ├── mini_orchestrator.py   # Task dataclass + the three implemented functions
│   ├── mock_detector.py       # lightweight stand-in detector (provided)
│   └── run_pipeline.py        # defines and runs the 4-task DAG (provided)
├── tests/test_smoke.py        # self-check tests
├── data/fixtures/             # personalized synthetic camera images + COCO annotations
├── _shared/                   # shared fixture generator + student-seed helper
├── generate_for_student.py    # generates data/fixtures from a student ID
├── batch_report.json          # pipeline output: per-image detection counts
├── dag_run_summary.json       # pipeline output: order + per-task status/attempts
├── NOTES.md                   # analysis (branch independence, retry cost)
└── requirements.txt
```
