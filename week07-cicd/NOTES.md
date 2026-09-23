# NOTES.md — Week 7: CI/CD Integration Testing

**Student ID used with `generate_for_student.py`:**
142602014


## Why gate integration-test on needs: [lint, unit-test]?

The integration-test job builds a full Docker image and spins up a container,
which costs real CI minutes (and wall-clock time — pulling the base image,
installing dependencies, waiting for health checks) compared to lint and
unit-test, which just run flake8/pytest against the interpreter directly.

If integration-test ran in parallel with lint and unit-test instead of after
them, every push/PR would pay that Docker build+run cost even when the code
has an obvious lint error or a failing unit test — cases where the container
was never going to be worth testing in the first place. Gating it behind
`needs: [lint, unit-test]` means the expensive job only runs once the cheap,
fast checks have already confirmed the code is at least superficially sound,
so broken code fails fast (in seconds) instead of burning minutes building
and running a container that was doomed anyway.
