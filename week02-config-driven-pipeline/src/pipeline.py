"""
The "after" version — YOUR file to complete.

Fill in the three functions marked with # TODO. Everything else (CLI wiring,
imports) is already done for you. Do not hardcode any path, format string, or
threshold value anywhere in this file — if you find yourself typing a literal
number or file path outside of a default/example, it belongs in the config
file instead.

Run with:
    python src/pipeline.py --config config/pipeline.yaml
"""
import argparse
import csv
import json

import yaml

REQUIRED_KEYS = ["input_path", "input_format", "high_value_threshold", "output_path"]


def load_config(path):
    """Load a YAML config file and validate required keys are present.

    Must raise ValueError naming the specific missing key if REQUIRED_KEYS
    are not all present. Do not let this fail with a bare KeyError later.
    """
    # TODO: implement
    try:
        with open(path,"r") as f:
            config=yaml.safe_load(f)
    except Exception as e:
        raise ValueError (f"failed to parse YAML: {e}")
    if not isinstance(config,dict):
        raise ValueError("Configuration file must parse into a dictionary.")
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ValueError(f"Missing required configuration key: '{key}'")
    return config

    


def load_transactions(path, fmt):
    """Load transactions from `path`, using `fmt` ("csv" or "json") to decide
    how to parse it — not by sniffing the file extension.

    Must return a list of dicts. Every dict must have at least "amount"
    (str or float) and "is_fraud" (str "True"/"False" or bool).
    Raise ValueError for any fmt other than "csv" or "json".
    """
    if fmt not in ["csv", "json"]:
        raise ValueError(f"Unsupported format: '{fmt}'. Must be 'csv' or 'json'.")

    transactions = []
    if fmt == "json":
        try:
            with open(path, "r", encoding="utf-8") as f:
                transactions = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to read or parse JSON file: {e}")
    else:
        try:
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                transactions = [dict(row) for row in reader]
        except Exception as e:
            raise ValueError(f"Failed to read or parse CSV file: {e}")

    if isinstance(transactions, dict):
        transactions = [transactions]
    if not isinstance(transactions, list):
        raise ValueError("Parsed data is not in an expected sequence layout")
    return transactions


def run_pipeline(config):
    """Load data per `config`, compute the same summary fields as
    pipeline_hardcoded.py (n_transactions, total_amount, fraud_rate,
    n_high_value, high_value_threshold), and write them as JSON to
    config["output_path"]. Return the report dict as well.
    """
    # TODO: implement
    input_path = config["input_path"]
    input_format = config["input_format"]
    threshold = float(config["high_value_threshold"])
    output_path = config["output_path"]

    transactions = load_transactions(input_path, input_format)
    n_transactions = len(transactions)
    total_amount = 0.0
    n_fraud = 0
    n_high_value = 0

    for tx in transactions:
        amt = float(tx.get("amount", 0))
        total_amount += amt

        is_fraud_raw = tx.get("is_fraud", False)
        if isinstance(is_fraud_raw, str):
            is_fraud = is_fraud_raw.strip().lower() in ["true", "1", "yes"]
        else:
            is_fraud = bool(is_fraud_raw)

        if is_fraud:
            n_fraud += 1
        if amt > threshold:
            n_high_value += 1

    fraud_rate = round(float(n_fraud) / n_transactions, 4) if n_transactions > 0 else 0.0
    report = {
        "n_transactions": n_transactions,
        "total_amount": round(total_amount, 2),
        "fraud_rate": fraud_rate,
        "n_high_value": n_high_value,
        "high_value_threshold": threshold,
    }

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        raise ValueError(f"Failed writing final pipeline execution report out: {e}")

    return report



def main():
    parser = argparse.ArgumentParser(description="Config-driven fraud transaction summary pipeline")
    parser.add_argument("--config", required=True, help="Path to a YAML config file")
    args = parser.parse_args()

    config = load_config(args.config)
    report = run_pipeline(config)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
