# CI verification

Fill this in after you push and watch the workflow run on GitHub (Actions
tab of your repo). This is how we confirm your CI actually ran green in a
real GitHub Actions runner, not just locally.

## Workflow run

Paste the URL of a successful run of all three jobs (Actions tab -> click
the run -> copy the URL):

```
https://github.com/PranavBK1/MLOPS_lab/actions/runs/35864502752
```

## Job summary

For each job, note pass/fail and how long it took:

- `lint`: pass — 8s
- `unit-test`: pass — 9s
- `integration-test`: pass — 25s

## What broke on the way there (optional but useful)

This repo is a personal monorepo (`MLOPS_lab`) with each week's lab in its
own subfolder, and this week's files live under `week07-cicd/`. GitHub
Actions only discovers workflow files under the repository's *top-level*
`.github/workflows/`, so the workflow initially registered but never
triggered a run (0 runs even after pushing). Fixed by adding a second
workflow file at the repo root (`.github/workflows/week07-ci.yml`) with
`working-directory: week07-cicd` and `paths: ["week07-cicd/**"]`, mirroring
`week07-cicd/.github/workflows/ci.yml` (which stays as-is for the
`tests/test_ci_config.py` self-check). See NOTES.md for more detail.
