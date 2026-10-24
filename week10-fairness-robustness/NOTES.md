# NOTES.md — Week 10: Fairness and Robustness Audit

**Student ID used with `generate_for_student.py`:** `142602014`

The generator derived seed `2066751499` and produced the committed 60-image
fixture set.

## Which classes got flagged?

At the 0.90 threshold, the audit flagged:

| Class | Detected / total | Recall |
|---|---:|---:|
| Bicycle | 11 / 14 | 0.7857 |
| MUV | 16 / 19 | 0.8421 |
| Two-wheeler | 14 / 16 | 0.8750 |

Bicycle and Two-wheeler are the expected misses: the fixture generator draws
these small-vehicle classes with much smaller boxes, which are harder for the
pixel-component detector to detect. MUV is an additional flagged class. With
only 19 examples, its result could reflect sampling noise or scene variation;
it is a reason to investigate and monitor, not proof of a systematic class
disparity. The audit measures recall, not demographic fairness.

## If the grouping variable were a protected attribute

If the groups represented protected demographics, a recall gap could mean
some people receive less reliable service or are exposed to greater risk. I
would need representative and lawfully collected evaluation data, privacy and
consent safeguards, uncertainty-aware reporting, and analysis of intersectional
groups and sample sizes. I would investigate causes, involve affected
stakeholders, document limitations, and mitigate and continuously monitor
harmful disparities before deployment. A vehicle class is not a substitute
for a protected group, and equalizing this synthetic metric does not establish
that a real system is fair.

## Which attack could corrupt this audit?

At the evaluation-data stage, data poisoning could alter fixture images or
COCO ground-truth boxes so the measured recall is silently too high or too
low, even though the audit code is unchanged. Dataset provenance and
versioning, access controls, and independent annotation/data-integrity checks
(for example, verifying a trusted manifest of file hashes) would make
unauthorized changes easier to detect and keep the evaluation set trustworthy.

## Would SHAP or LIME explain a missed detection?

For a concrete miss, `camera_A_daylight/026.jpg` has a MUV ground-truth box
`[60, 28, 33, 28]`. Its best detector box has IoU `0.0814`, below the `0.3`
matching threshold. Only 323 of the 924 pixels in that ground-truth region
meet the detector's reddish-pixel rule, and the four emitted boxes do not
localize the ground-truth object closely enough.

SHAP or LIME would not directly answer why this bounding-box detector missed
that object. They generally need a fixed, meaningful output to explain, while
an object detector returns a variable set of boxes, classes, and scores; box
generation and filtering can change discontinuously when image pixels are
perturbed. One could define a scalar target for a fixed candidate box and
explain that target, but it would not automatically explain the absence of a
matching detection. Here, inspecting the rule, connected components, and
overlap is more direct. For a learned detector, I would use a detector-aware
explanation method tied to a specified location/class score and validate it
against occlusion or counterfactual tests.

## What did your attack show?

The flagged classes' recall by perturbation budget is:

| Class | Clean (0) | ε=10 | ε=20 | ε=30 | ε=40 |
|---|---:|---:|---:|---:|---:|
| Bicycle | 0.7857 | 0.6429 | 0.6429 | 0.2143 | 0.1429 |
| MUV | 0.8421 | 0.7895 | 0.6842 | 0.5789 | 0.3684 |
| Two-wheeler | 0.8750 | 0.6875 | 0.6250 | 0.3750 | 0.2500 |

Bicycle falls at ε=10, stays level at ε=20, then falls again at ε=30 and 40.
MUV and Two-wheeler fall at every tested increase in ε. At ε=20 the largest
recall drop is Two-wheeler (0.2500), followed by Three-wheeler (0.2143) and
Tempo-traveller (0.2106). Two-wheeler was also flagged in the clean audit, but
the other two were not. The classes with the lowest absolute recall at ε=20
are Two-wheeler (0.6250), Bicycle (0.6429), and MUV (0.6842). Therefore the
relative-drop and absolute-recall rankings do not agree. Absolute recall is
more directly informative about which class has the poorest performance at a
given operating condition; the drop ranking reveals sensitivity to the
perturbation. Both matter: an attack or unmonitored failure can impose the
greatest cost on groups that already have poor baseline performance, even if
they are not the most fragile by relative change.

For this rule-based detector, adversarial training could expose a detector
being trained to varied color shifts and perturbations while retaining
ground-truth boxes, then test the same per-class recall across held-out
perturbation budgets. Input validation could check image mode, dimensions,
channel ranges, and unexpected global color shifts and alert or reject
out-of-policy inputs; it should not be treated as a defense against every
localized attack. This rule is brittle because its decision depends directly
on fixed per-pixel red and channel-difference thresholds. A small color change
can remove pixels from a connected component, fragment it, or shrink it below
the detector's minimum size. A CNN can learn more distributed features and
may be less sensitive to this exact color rule, but it is not inherently
robust: it also needs threat-model-specific training, validation, and
monitoring.
