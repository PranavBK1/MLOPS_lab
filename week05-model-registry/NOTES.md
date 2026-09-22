# NOTES.md — Week 5: Model Registry Governance

**Student ID used with `generate_for_student.py`:**
<!-- REQUIRED: replace this line with the exact --student-id value you passed to
     generate_for_student.py. The grader re-runs that command with this value and
     diffs the result against the committed data/ directory, so it must match
     character-for-character (roll number or institute email). -->
142602014


## Which candidate reached Production, and why?

`candidate_b` reached Production, registered as version **v2**.

The pipeline registers both candidates, then makes three promotion attempts:

1. `promote_model("fraud-detector", v1, "Production")` with no model card yet —
   blocked by `GovernanceError` ("no model_card.json for this version").
2. Same call after a card is written for v1 — still blocked, because
   `candidate_a`'s `f1 = 0.557` is below `PRODUCTION_F1_THRESHOLD = 0.70`.
3. `promote_model("fraud-detector", v2, "Production")` after writing v2's card —
   succeeds: v2 has a complete model card **and** `f1 = 0.826 >= 0.70`, so both
   governance conditions pass.

`get_production_model` then returns v2, and `registry_summary.json` records
`production_version = "v2"` with `f1 = 0.826`. No earlier version was in
Production, so nothing had to be auto-archived on this run.


## Gating stale feature data

`promote_model` would need a third independent condition in its Production gate,
plus a piece of provenance it does not currently record:

- **Capture the data date at registration.** `register_model` would store the
  feature-data cutoff in the manifest, e.g.
  `manifest["feature_data_as_of"] = <ISO date>`, read from the model artifact or
  passed in alongside `metrics`. Without this timestamp there is nothing to
  check against.
- **New constant:** `STALE_FEATURE_DATA_MAX_AGE_DAYS = 30`.
- **New gate check** (only for `target_stage == "Production"`, evaluated
  independently of the card and f1 checks so the error message says which one
  failed): parse `feature_data_as_of`, compute
  `age = _now_date() - feature_data_as_of`, and
  `raise GovernanceError(...)` if `age > timedelta(days=30)` or if the field is
  missing entirely (fail closed — unknown provenance is not promotable).
- **Optional but realistic:** re-run the same staleness check on a schedule for
  whatever is already in Production, so a model that was fresh at promotion time
  but has since aged past 30 days gets flagged or auto-archived rather than
  silently rotting.


## Scaling the gate to 40 candidates

**What genuinely would not change:**

- `register_model` is already per-version, append-only, and immutable. Calling
  it 40 times just produces `v1`…`v40` with no overwrites; cost is linear and
  each version is independent.
- `promote_model`'s gate logic (card present + `f1 >= threshold` + archive the
  previous Production version) does not depend on how many candidates exist. It
  still only ever moves *one* version to Production, and "at most one Production
  version" still holds.
- `get_production_model` still returns exactly one manifest (or `None`).
  Promotion stays a single deliberate, gated action regardless of how many
  candidates are sitting in `None`/`Staging`.

**What would need to change / what starts to hurt:**

- `get_production_model` and the "archive the previous Production version" loop
  both do a full directory scan plus a JSON read per version — O(n) per call.
  Fine at 40, but at scale you would keep a single top-level pointer file
  (`current_production.json`) that names the live version, and update it on
  promotion, instead of re-scanning every time.
- You would not hand-register 40 candidates one call at a time. `register_model`
  (or a wrapper) would take the whole HPO/AutoML result set and a selection
  step — e.g. keep only the top-k by validation metric — so the registry stores
  the few worth keeping, not all 40 near-identical runs.
- The **model-card requirement becomes the real bottleneck**, not the code.
  Writing 40 genuine, model-specific cards by hand does not scale, so you would
  attach one shared card template per search (intended use, training data,
  limitations, ethical considerations are identical across the sweep) and only
  require per-version deltas — metrics and hyperparameters — to be filled in.
  The "must actually be filled in, not just present" rule stays; only its
  granularity changes.
