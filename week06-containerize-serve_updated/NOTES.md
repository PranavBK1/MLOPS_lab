# NOTES.md — Week 6: Containerize and Serve a Detector

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
student-id: 142602014
seed: 3805092634
Wrote 6 images across 2 camera profiles -> C:\Users\Pranav\Downloads\week06-containerize-serve_updated\data\fixtures
Wrote 28 annotations -> C:\Users\Pranav\Downloads\week06-containerize-serve_updated\data\fixtures/_annotations.coco.json


## Built image size

<!-- What image size did `docker images` report for week6-detector? -->
IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
week6-detector:latest   61f70491228f        246MB         60.3MB    U   


## Swapping in a real checkpoint

<!-- What's the single biggest thing you'd change about this Dockerfile if
     src/mock_detector.py were swapped for a real torch-based checkpoint?
     (Think about what that does to build time and image size.) -->

The base image: `python:3.11-slim` is fine for Flask + Pillow, but torch +
a detection framework (ultralytics/mmdetection) plus their transitive deps
would balloon the image from tens of MB to multiple GB (torch's CUDA wheels
alone are ~2-3GB), and `pip install` at build time would go from seconds to
minutes. I'd switch to a multi-stage build off an official CUDA/PyTorch base
image (or a CPU-only torch build if no GPU is available at serve time), pin
exact package versions to keep the layer cache useful across rebuilds, and
make sure the model checkpoint itself is fetched/mounted separately (a
volume or a download step) rather than baked into the image, so app-code
changes don't force a multi-GB re-download/re-push every time.
