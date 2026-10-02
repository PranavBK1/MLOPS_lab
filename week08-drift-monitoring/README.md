# Week 8 — Drift and Observability Monitoring

**DS5619 Machine Learning Systems Operations · Track B (BMD-45 vehicle detection)**

This project monitors a vehicle detector for **distribution drift** using the
**Population Stability Index (PSI)**. The detector's confidence scores are
the monitored feature, since a production system has them at inference time
even when it has no ground-truth labels yet.

Two synthetic CCTV "cameras" stand in for the train/deploy domain shift
reported in the BMD-45 paper (~33.6% mAP cross-domain vs ~83.8% in-domain):

- `camera_A_daylight` is the **reference** distribution: bright background,
  low noise, full-size vehicles.
- `camera_B_lowlight` is the **live** traffic being monitored: dark
  background, heavy noise, vehicles scaled to 0.7×.

## Result

| | camera_A_daylight (reference) | camera_B_lowlight (live) |
|---|---|---|
| detections | 83 | 80 |
| mean confidence | 0.9750 | 0.9789 |
| std | 0.0301 | 0.0096 |
| min / max | 0.778 / 0.98 | 0.894 / 0.98 |

**PSI = 0.1916 → drift level: `moderate`** (thresholds: 0.10 moderate, 0.25 significant)

The mean barely changes, but the *shape* of the distribution does: the
reference camera's low-confidence tail disappears in the live data. PSI
catches this and a simple mean-based alert would not. See
[NOTES.md](NOTES.md) for the full analysis, including which kinds of drift
confidence-only monitoring can and can't detect.

## What was done

1. **Generated personalized data:** ran
   `generate_for_student.py --student-id 142602014`, which writes 20
   synthetic images per camera plus `_annotations.coco.json` into
   `data/fixtures/`. The data is seeded deterministically from the student
   ID (seed `336154273`).
2. **Implemented the four functions in `src/drift_monitor.py`:**
   - `extract_confidence_scores(camera_dir)` loads every `*.jpg` in sorted
     order (so results are deterministic), runs the mock detector on each,
     and returns a flat list of the detection scores as floats.
   - `compute_psi(reference, live, n_bins=10)` splits [0, 1] into
     equal-width bins and puts a score of exactly 1.0 in the last bin. It
     turns the counts into proportions, clamps each proportion to at least
     1e-4, and returns `Σ (live − ref) · ln(live / ref)`.
   - `classify_drift(psi)` returns `"none"` below 0.10, `"moderate"` from
     0.10 up to (but not including) 0.25, and `"significant"` at 0.25 and
     above. Both boundaries are inclusive on the upper band.
   - `summarize_scores(scores)` returns count, mean, std, min and max,
     rounded to 4 decimals. When there is only one score, std is 0.0
     instead of raising an error.
3. **Ran the pipeline** (`src/run_pipeline.py`), which wrote
   `drift_report.json`.
4. **Verified:** all 9 self-check tests in `tests/test_smoke.py` pass, and
   the PSI matches the value the data generator computed independently
   (0.1916).
5. **Wrote [NOTES.md](NOTES.md):** it covers the observed drift level, why
   it matches expectations, and why confidence-score monitoring catches
   data/prediction drift but misses **concept drift** (and label drift).
   It also lists what to monitor once ground-truth labels arrive.

## Project structure

```
├── src/
│   ├── drift_monitor.py      # the four implemented functions
│   ├── mock_detector.py      # lightweight stand-in detector (provided)
│   └── run_pipeline.py       # driver that writes drift_report.json (provided)
├── tests/test_smoke.py       # self-check tests
├── data/fixtures/            # personalized synthetic camera images + COCO annotations
├── _shared/                  # shared fixture generator + student-seed helper
├── generate_for_student.py   # generates data/fixtures from a student ID
├── drift_report.json         # pipeline output
├── NOTES.md                  # analysis
└── requirements.txt
```

## How to run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python generate_for_student.py --student-id 142602014   # regenerate data
python src/run_pipeline.py                              # writes drift_report.json
pytest tests/ -q                                        # 9 passed
```

## References

- Week 8 lecture: ML Observability and Drift Detection (PSI, univariate feature drift).
- Sharma et al., "BMD-45: A Large-Scale CCTV Vehicle Detection Dataset for
  Urban Traffic," CVPR 2026 Findings.
