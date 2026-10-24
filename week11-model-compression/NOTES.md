# NOTES.md — Week 11: Model Compression Benchmark

**Student ID used with `generate_for_student.py`:**
142602014

(seed: 3543197396, salt `week11`)

## Results at the default 70% sparsity

| variant            | size_bytes | ratio | accuracy |
|--------------------|-----------:|------:|---------:|
| baseline_fp32      | 1024       | 1.00x | 100.00%  |
| pruned_dense_fp32  | 1024       | 1.00x | 99.67%   |
| pruned_sparse_coo  | 616        | 1.66x | 99.67%   |
| quantized_int8     | 256        | 4.00x | 99.33%   |

Latency comes out at about 4.3 ms per pass for every variant. As the README
says, that's because this implementation runs pure Python on dequantized
floats. It is not a real result about speed.

## pruned_dense_fp32 vs. pruned_sparse_coo

Both rows hold exactly the same weights: 179 of the 256 are zeroed and 77
survive. Because the arithmetic is identical, so is the accuracy (99.67%).
The size is different because of how the zeros are stored.

- **Dense FP32** still stores all 256 slots at 4 bytes each, so a zero costs as
  much as any other value: 256 × 4 = **1024 bytes**. That's the same as the
  baseline. This is the pruning pitfall from the lecture: pruning only marks
  weights as zero. It saves no memory, bandwidth or disk unless the storage
  format (or the kernel) knows how to skip zeros.
- **Sparse COO** stores only the non-zero entries, and each one pays for its
  value (4 B) plus its index (4 B): 77 × 8 = **616 bytes**, which is 1.66x
  smaller.

The index overhead also limits how much COO can save. Each survivor costs
8 bytes instead of 4, so COO only beats dense storage once more than 50% of
the weights are zero. At 70% sparsity the saving is real but modest (1.66x).
INT8 quantization of the unpruned model gets 4x without changing the format at
all.

## The 0.95-sparsity experiment

I set `PRUNE_SPARSITY = 0.95` in `src/run_pipeline.py`, re-ran the pipeline,
then set it back to 0.70 for the committed report:

| variant            | size_bytes | ratio | accuracy |
|--------------------|-----------:|------:|---------:|
| baseline_fp32      | 1024       | 1.00x | 100.00%  |
| pruned_dense_fp32  | 1024       | 1.00x | **81.33%** |
| pruned_sparse_coo  | 104        | 9.85x | **81.33%** |
| quantized_int8     | 256        | 4.00x | 99.33%   |

Accuracy drops from 99.67% to 81.33%. At 95% sparsity, `int(0.95 × 256) = 243`
weights are zeroed and only 13 survive. Only 40 of the 256 weights are
informative (|w| ≥ 0.5), and the other 216 are noise (|w| < 0.03).

- At 70%, pruning zeroes 179 weights, all of them below the 216 noise weights,
  so every informative weight survives. Only noise is removed, and accuracy
  barely moves.
- At 95%, pruning has to zero all 216 noise weights and then 27 of the 40
  informative ones (the smallest of them). The model is left with 13 of its
  40 useful weights, so part of the real decision function is gone, and the
  examples that depended on those 27 weights are now misclassified.

So the cliff falls where sparsity passes 216/256 ≈ 84%. Up to that point
pruning removes weights that "don't earn their byte". Past it, pruning starts
removing signal. The 9.85x size reduction is not worth an 18-point accuracy
loss. A trade-off like this is why compression is treated as a Pareto frontier
and not as a case of "smaller is better".
