# NOTES.md — Week 3: ETL and Data Validation

**Student ID used with `generate_for_student.py`:**
python generate_for_student.py --student-id 142602014
student_id: 142602014
seed: 2313628625


## Quarantine count vs. the 7 known injected problems

<!-- How many rows ended up quarantined, and does that match the 7 known
     injected problems? (It won't match exactly — some rows may trip more
     than one expectation. Explain the discrepancy if there is one.) -->
## Quarantine count vs. the 7 known injected problems

**Quarantined Row Count:** 6 rows  
**Total Violations Detected:** 8 violations  

### Explanation of Discrepancy
The number of quarantined rows (**6**) does not equal the total number of detected violations (**8**) due to expectation overlap on specific rows:

* **Overlapping Violations:** Rows `224` and `228` (which have missing `amount` values) failed two expectations at the same time: `expect_column_not_null` and `expect_column_positive`. This produced 4 total violation records across just 2 physical rows.
* **Quarantine Deduplication:** The ETL pipeline quarantines a row if it trips *at least one* expectation. Because multi-failing rows (224 and 228) are only routed to `quarantined_transactions.csv` once, the 8 total violation flags condense down to **6 unique quarantined rows** (row indices `28`, `38`, `46`, `224`, `228`, and `594`).