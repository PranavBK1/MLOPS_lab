"""
Extract -> Validate -> Transform -> Load pipeline for the fraud transaction
data. Run with:

    python src/etl.py --config config.yaml

(a default config.yaml pointing at data/raw_transactions.csv is provided)
"""
import argparse
import csv
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import expectations as exp

KNOWN_CATEGORIES = {
    "grocery", "electronics", "fuel", "travel", "restaurant",
    "online_retail", "utilities", "pharmacy", "entertainment", "atm_withdrawal",
}


def build_expectation_suite():
    """The data contract for this dataset. Each entry says which expectation
    function to run, and with what arguments. This is provided — read it to
    know exactly what your expectation functions in expectations.py need to
    handle correctly.
    """
    return [
        (exp.expect_column_not_null, {"column": "amount"}),
        (exp.expect_column_not_null, {"column": "card_id"}),
        (exp.expect_column_positive, {"column": "amount"}),
        (exp.expect_column_in_set, {"column": "merchant_category", "allowed_values": KNOWN_CATEGORIES}),
        (exp.expect_column_unique, {"column": "transaction_id"}),
    ]


def extract(input_path):
    with open(input_path, newline="") as f:
        return list(csv.DictReader(f))


def run_etl(config):
    """Implement the four ETL steps described in ASSIGNMENT.md:
    extract, validate (run every expectation in build_expectation_suite()
    and collect ALL violations, not just the first), transform (split into
    clean vs quarantined rows — a row with ANY violation is quarantined),
    load (write clean_output_path, quarantine_output_path, and
    report_output_path as described in the assignment).

    Return the validation_report dict as well as writing it to disk.
    """

    # ---------------------------------------------------------
    # 1. Extract
    # ---------------------------------------------------------
    rows = extract(config["input_path"])

    # ---------------------------------------------------------
    # 2. Validate
    # ---------------------------------------------------------
    suite = build_expectation_suite()

    all_violations = []

    report = {
        "expectations": []
    }

    for expectation_func, kwargs in suite:
        violations = expectation_func(rows, **kwargs)
        all_violations.extend(violations)

        report["expectations"].append({
            "expectation": expectation_func.__name__,
            "column": kwargs["column"],
            "n_violations": len(violations),
            "row_indices": [v.row_index for v in violations],
        })

    # ---------------------------------------------------------
    # 3. Transform
    # ---------------------------------------------------------
    violated_rows = {v.row_index for v in all_violations}

    clean_rows = []
    quarantined_rows = []

    for i, row in enumerate(rows):
        if i in violated_rows:
            quarantined_rows.append(row)
        else:
            clean_rows.append(row)

    # ---------------------------------------------------------
    # 4. Load
    # ---------------------------------------------------------
    clean_path = config["clean_output_path"]
    quarantine_path = config["quarantine_output_path"]
    report_path = config["report_output_path"]

    # Make sure output directories exist.
    for path in (clean_path, quarantine_path, report_path):
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    # Write clean and quarantined CSV files.
    fieldnames = rows[0].keys() if rows else []

    with open(clean_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_rows)

    with open(quarantine_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(quarantined_rows)

    # Add overall summary to the report.
    report["summary"] = {
        "total_rows": len(rows),
        "clean_rows": len(clean_rows),
        "quarantined_rows": len(quarantined_rows),
        "total_violations": len(all_violations),
    }

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    report = run_etl(config)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()