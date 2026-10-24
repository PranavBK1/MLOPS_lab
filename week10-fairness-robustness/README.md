# Week 10: Fairness and Robustness Audit

This lab audits the mock BMD-45 vehicle detector for per-class recall
disparities, then measures how an FGSM-style colour perturbation changes those
recalls. The fixtures are synthetic and personalized by student ID.

## Setup and run

From this directory, install the dependencies and generate your fixtures:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python generate_for_student.py --student-id 142602014
python src/run_pipeline.py
pytest tests/ -q
```

The generator writes 60 images and their COCO annotations under
`data/fixtures/`. The pipeline writes the clean per-class recall, flagged
classes, and adversarial results to `fairness_report.json`.

## Audit design

Ground-truth boxes are matched against any detector box using intersection over
union (IoU), regardless of the detector's predicted category. Recall is
aggregated by the ground-truth category name. Categories below the 0.90 recall
threshold are flagged, with lower recall listed first.

The robustness check lowers red and raises green and blue by a specified
per-channel budget, clamped to the 0–255 range, and reruns the same audit. This
is a white-box perturbation tailored to the mock detector's hand-written
reddish-pixel rule; it is not a realistic attack evaluation of a trained
object-detection model.

## Fairness framing

This exercise groups by vehicle class because the dataset has no demographic
attributes. Real fairness audits often compare outcomes across protected
demographic groups, where disparities have substantially different ethical and
legal consequences. See [NOTES.md](NOTES.md) for the interpretation of this
student's results and the limitations of the audit.

The assignment instructions are included in [README.pdf](README.pdf).
