# NOTES.md — Week 8: Drift and Observability Monitoring

**Student ID used with `generate_for_student.py`:** `142602014`

(Derived seed: `336154273`, salt `week08`. Regenerate with
`python generate_for_student.py --student-id 142602014`.)


## Drift level vs. expectation

`drift_report.json` shows **PSI = 0.1916 → drift level: `moderate`**
(moderate band is 0.10 ≤ PSI < 0.25).

| | camera_A_daylight (reference) | camera_B_lowlight (live) |
|---|---|---|
| detections | 83 | 80 |
| mean score | 0.9750 | 0.9789 |
| std | 0.0301 | 0.0096 |
| min / max | 0.778 / 0.98 | 0.894 / 0.98 |

Yes, this is what I'd expect. The two cameras were built with deliberately
different visual statistics (dark background, 2.75× more pixel noise, boxes
scaled to 0.7×), so the input distribution has clearly shifted and the
detector's output distribution shifts with it. The drift is "moderate"
rather than "significant" because the mock detector's confidence is
mostly driven by how solidly a red blob fills its bounding box, and that
saturates near the 0.98 cap under both conditions.

The *mean* barely moves (0.975 vs 0.979, live is even slightly higher),
yet PSI still flags drift because it compares the whole binned shape:
camera A has a tail of lower-confidence detections (down to 0.778) that
camera B doesn't have, so the 0.7–0.9 bins are emptied out in the live
data. A simple "alert if mean confidence drops" rule would have missed
this entirely, which is a good argument for distribution-level metrics like
PSI. Also note that higher confidence on the low-light camera is *not*
evidence that the model is doing better there — confidence is not
accuracy.


## What confidence-score-only monitoring misses

Confidence-score PSI is a **prediction (output) drift** signal, and through
it an indirect proxy for **data / covariate drift** — a change in P(X),
the input distribution (here: brightness, noise, object size). It needs no
labels, which is why it's useful in real time.

What it **cannot** catch is **concept drift** — a change in P(Y | X), the
relationship between inputs and the correct answer. If the model keeps
producing the same confidence distribution while being confidently
*wrong* (e.g. new vehicle types it labels as "Sedan", a camera re-angled so
boxes are misplaced, label definitions changing), confidence PSI stays
near 0. A detector can be confidently wrong, and an overconfident model
failing on a new domain is exactly the BMD-45 33.6% vs 83.8% mAP story.
It also can't see **label / prior drift** (P(Y): class mix changing,
e.g. more two-wheelers), since `category_id` isn't monitored here.

With ground-truth labels arriving a day later, I would additionally monitor:

1. **Actual performance per camera and per day** — mAP@0.5 / mAP@0.5:0.95,
   precision and recall, compared to the reference camera's baseline.
   This is the only direct way to detect concept drift.
2. **Per-class metrics and the class distribution** — per-class
   recall/AP and PSI on predicted vs. true class frequencies (label drift).
3. **Missed detections (false negatives)** — count of GT boxes with no
   matching prediction. Confidence-only monitoring is blind to these by
   construction: a vehicle the model never detects produces no score at all
   (in this run, 158 GT boxes vs. 163 detections hides both misses and
   false positives).
4. **Calibration** — reliability diagram / expected calibration error
   (does a 0.95 score really mean ~95% precision?), so I know whether
   confidence drift can be trusted as a proxy for accuracy.
5. **Input feature drift directly** — image brightness, contrast, noise
   level and box-size distributions, for an earlier and more explainable
   signal of *why* the outputs moved.
