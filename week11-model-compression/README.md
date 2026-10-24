# Lab 11: Model Compression Benchmark

Track B (BMD-45 vehicle detection) · Week 11 · DS5619 Machine Learning Systems Operations

This is a small model-compression benchmark with no dependencies beyond the
standard library. It applies **magnitude-based pruning** and **symmetric INT8
quantization** to a 256-weight linear classifier, which stands in for a
detector's classification head. Only 40 of its weights are informative. The
benchmark measures **size, accuracy and latency** for four variants.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python generate_for_student.py --student-id 142602014
```

`generate_for_student.py` writes `data/weights.json` and `data/eval_data.json`,
seeded deterministically from the student ID. The ID I used is recorded in
[NOTES.md](NOTES.md).

## Run

```bash
python src/run_pipeline.py   # writes compression_report.json
pytest tests/ -q             # self-check (13 tests)
```

## Repository layout

| Path | Purpose |
|------|---------|
| `src/compression.py` | `model_size_bytes`, `prune_weights`, `sparse_coo_size_bytes`, `quantize_int8`, `benchmark_model` (implemented), plus the given `predict` / `dequantize_int8` |
| `src/run_pipeline.py` | Driver script that benchmarks the four variants (unchanged) |
| `generate_for_student.py` | Generates per-student weights and eval data |
| `_shared/student_seed.py` | Turns a student ID into a deterministic seed |
| `data/` | Generated weights and the 300-example eval set |
| `compression_report.json` | Pipeline output (deliverable) |
| `NOTES.md` | Analysis: dense vs. sparse pruning, and the 0.95-sparsity cliff |
| `tests/test_smoke.py` | Self-check tests |

## Results (70% sparsity)

| variant            | size_bytes | ratio | accuracy |
|--------------------|-----------:|------:|---------:|
| baseline_fp32      | 1024       | 1.00x | 100.00%  |
| pruned_dense_fp32  | 1024       | 1.00x | 99.67%   |
| pruned_sparse_coo  | 616        | 1.66x | 99.67%   |
| quantized_int8     | 256        | 4.00x | 99.33%   |

- **Pruning pitfall:** pruned weights stored densely take up exactly the same
  bytes as the baseline. The size only shrinks with a sparse (COO) format.
- **INT8** gives a 4x size reduction and loses 0.67 points of accuracy.
- **95% sparsity** drops accuracy to 81.33%, because pruning then removes 27 of
  the 40 informative weights. See [NOTES.md](NOTES.md).

Latency is about the same for every variant. This pure-Python implementation
dequantizes INT8 back to floats before doing any arithmetic, so the latency
numbers say nothing about real INT8 speedups.
