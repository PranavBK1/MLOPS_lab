# NOTES.md — Week 4: Versioning, Feature Store & Lineage

**Student ID used with `generate_for_student.py`:**
142602014


## v1 vs. v2 manifest comparison

<!-- What's different between the v1 and v2 feature group's manifest.json?
     (Look at both.) -->(you'll mainly see feature_group_version_id, source_raw_version_id, and row_count differ, while schema stays the same since build_features normalizes both schemas to the same output keys).


## Why treat amount_minor_units differently from amount?

<!-- Why does build_features need to treat amount_minor_units differently
     from amount for the aggregates to be comparable across versions? -->
     because v2's amount is expressed in integer cents while v1's is a float in whole currency units; averaging/maxing them together without converting would make v2's numbers look 100x larger than v1's, so they wouldn't be comparable across versions.



# Project Notes: Data Versioning & Feature Store

## Architectural Decisions
- **SHA-256 Data Integrity:** Generated cryptographic hashes for all incoming raw transaction files (`v1` and `v2`). This guarantees detection of data drift or corruption at the source.
- **Decoupled Feature Storage:** Separated raw dataset manifests (`.feature_store/raw_versions`) from computed feature sets (`.feature_store/feature_groups`).
- **Data Lineage:** Linked every calculated feature group version explicitly to its source raw dataset version via `raw_version_lineage` metadata.

## Key Learnings
1. **Raw vs. Feature Versioning:** Raw versioning captures dynamic, immutable log updates over time. Feature versioning tracks structural calculations and aggregation logic derived from raw logs.
2. **Reproducibility:** By storing explicit lineage maps (`lineage_report.json`), ML engineers can recreate exact training sets for old model versions without training-serving skew.
3. **Schema Evolution:** When moving from raw `v1` to `v2`, missing or extra transaction columns require normalization during feature engineering to maintain downstream schema consistency.