import sys
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta

# ------------------------------------------------------------
# FINSHIELD AI - AML EDGE-CASE TESTING (10 ADDITIONAL SCENARIOS)
# ------------------------------------------------------------

# This file is intended to be placed inside the ml folder:
# code/ml/test_aml_edge_cases.py

ML_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ML_DIR))

from src.analysis_aml import analyze_aml


BASE_TIME = datetime(2026, 10, 29, 10, 0)


def timestamp(value):
    return value.strftime("%Y/%m/%d %H:%M")


def create_transaction(sender, receiver, amount, time=None):
    return {
        "timestamp": timestamp(time or BASE_TIME),
        "sender_id": sender,
        "sender_account": sender,
        "receiver_id": receiver,
        "receiver_account": receiver,
        "amount": amount,
        "currency": "USD",
        "payment_type": "TRANSFER"
    }


def make_history(sender, entries):
    """
    entries: list of (receiver, amount, datetime_object)
    """
    return [
        create_transaction(sender, receiver, amount, time)
        for receiver, amount, time in entries
    ]


def score_is_valid(result):
    score_keys = ("rule_score", "behavior_score", "network_score", "aml_score")
    for key in score_keys:
        value = float(result[key])
        if not 0.0 <= value <= 1.0:
            return False, f"{key} is outside [0, 1]: {value}"
    return True, "All scores are within [0, 1]."


def run_valid_case(name, transaction, history, checks=None):
    """Run a valid-input test and apply basic score/output checks."""
    try:
        result = analyze_aml(transaction, history)
        valid, message = score_is_valid(result)

        if not valid:
            return {
                "name": name, "status": "FAIL",
                "details": message, "result": result
            }

        if not isinstance(result.get("triggered_rules"), list):
            return {
                "name": name, "status": "FAIL",
                "details": "triggered_rules is not a list.", "result": result
            }

        if not isinstance(result.get("notification"), dict):
            return {
                "name": name, "status": "FAIL",
                "details": "notification is not a dictionary.", "result": result
            }

        if checks:
            for check_name, check in checks.items():
                passed, detail = check(result)
                if not passed:
                    return {
                        "name": name, "status": "FAIL",
                        "details": f"{check_name}: {detail}", "result": result
                    }

        return {
            "name": name, "status": "PASS",
            "details": message, "result": result
        }

    except Exception as exc:
        return {
            "name": name, "status": "FAIL",
            "details": f"{type(exc).__name__}: {exc}", "result": None
        }


def run_invalid_case(name, transaction, history=None):
    """
    Invalid-input diagnostic.
    REJECTED is the desired result for invalid data.
    REVIEW means the current module accepted the data; inspect validation.
    """
    try:
        result = analyze_aml(transaction, history or [])
        return {
            "name": name,
            "status": "REVIEW",
            "details": (
                "The AML function accepted this input. Check whether input "
                "validation should reject it. Returned score: "
                f"{result.get('aml_score')}"
            ),
            "result": result
        }
    except (TypeError, ValueError, KeyError) as exc:
        return {
            "name": name,
            "status": "PASS",
            "details": f"Invalid input was rejected: {type(exc).__name__}: {exc}",
            "result": None
        }
    except Exception as exc:
        return {
            "name": name,
            "status": "REVIEW",
            "details": (
                "The input raised an unexpected exception: "
                f"{type(exc).__name__}: {exc}"
            ),
            "result": None
        }


def main():
    results = []

    # 16. Empty transaction object: should be rejected by input validation.
    results.append(run_invalid_case(
        "16 - Empty transaction input",
        {},
        []
    ))

    # 17. Missing required sender/receiver/amount fields.
    results.append(run_invalid_case(
        "17 - Missing required transaction fields",
        {"timestamp": timestamp(BASE_TIME), "currency": "USD"},
        []
    ))

    # 18. Zero amount: valid numeric edge case; should not crash or create
    # an amount-based high-risk rule.
    results.append(run_valid_case(
        "18 - Zero transaction amount",
        create_transaction("S18", "R18", 0),
        [],
        {
            "score bounds": lambda r: score_is_valid(r),
            "no high amount rule": lambda r: (
                "HIGH_AMOUNT" not in r.get("triggered_rules", []),
                "HIGH_AMOUNT was triggered for amount 0."
            )
        }
    ))

    # 19. Negative amount: should ideally be rejected by validation.
    results.append(run_invalid_case(
        "19 - Negative transaction amount",
        create_transaction("S19", "R19", -500),
        []
    ))

    # 20. Exactly 24 hours before the current transaction.
    history_20 = make_history("S20", [
        ("R20", 1000, BASE_TIME - timedelta(hours=24)),
        ("R20", 1000, BASE_TIME - timedelta(hours=12)),
        ("R20", 1000, BASE_TIME - timedelta(hours=6)),
        ("R20", 1000, BASE_TIME - timedelta(hours=1))
    ])
    results.append(run_valid_case(
        "20 - Exact 24-hour frequency boundary",
        create_transaction("S20", "R20", 1000),
        history_20
    ))

    # 21. All four previous transactions are just outside the 24-hour window.
    history_21 = make_history("S21", [
        ("R21", 1000, BASE_TIME - timedelta(hours=24, minutes=1)),
        ("R21", 1000, BASE_TIME - timedelta(hours=25)),
        ("R21", 1000, BASE_TIME - timedelta(hours=26)),
        ("R21", 1000, BASE_TIME - timedelta(hours=27))
    ])
    results.append(run_valid_case(
        "21 - Transactions just outside 24-hour window",
        create_transaction("S21", "R21", 1000),
        history_21,
        {
            "frequency should not trigger": lambda r: (
                "HIGH_FREQUENCY" not in r.get("triggered_rules", []),
                "HIGH_FREQUENCY triggered although fewer than five "
                "transactions should be inside the 24-hour window."
            )
        }
    ))

    # 22. Large history: checks that analysis can process many records.
    history_22 = []
    for i in range(1000):
        tx_time = BASE_TIME - timedelta(days=2, minutes=i)
        history_22.append(
            create_transaction(
                "S22", f"R22_{i % 20}", 1000 + (i % 10), tx_time
            )
        )
    results.append(run_valid_case(
        "22 - Large transaction history (1,000 records)",
        create_transaction("S22", "R22_0", 1000),
        history_22
    ))

    # 23. Duplicate historical transactions: checks stability and score bounds.
    duplicate = create_transaction(
        "S23", "R23", 1000, BASE_TIME - timedelta(hours=2)
    )
    history_23 = [dict(duplicate) for _ in range(6)]
    results.append(run_valid_case(
        "23 - Duplicate historical transactions",
        create_transaction("S23", "R23", 1000),
        history_23
    ))

    # 24. Many rule/network indicators: scores must remain capped at 1.0.
    history_24 = []
    for i in range(12):
        history_24.append(
            create_transaction(
                "S24", f"R24_{i}", 1000,
                BASE_TIME - timedelta(minutes=30 + i)
            )
        )
    # Add incoming edges to the current receiver and a reciprocal edge.
    for i in range(6):
        history_24.append(
            create_transaction(
                f"S24_IN_{i}", "R24_NEW", 1000,
                BASE_TIME - timedelta(hours=2 + i)
            )
        )
    history_24.append(
        create_transaction(
            "R24_NEW", "S24", 1000, BASE_TIME - timedelta(hours=1)
        )
    )
    results.append(run_valid_case(
        "24 - Rule and network score capping",
        create_transaction("S24", "R24_NEW", 200000),
        history_24,
        {
            "score caps": lambda r: score_is_valid(r),
            "high amount should trigger": lambda r: (
                "HIGH_AMOUNT" in r.get("triggered_rules", []),
                "HIGH_AMOUNT was not triggered."
            )
        }
    ))

    # 25. Invalid timestamp: should ideally be rejected by validation.
    results.append(run_invalid_case(
        "25 - Invalid timestamp format",
        {
            "timestamp": "not-a-valid-date",
            "sender_id": "S25",
            "sender_account": "S25",
            "receiver_id": "R25",
            "receiver_account": "R25",
            "amount": 1000,
            "currency": "USD",
            "payment_type": "TRANSFER"
        },
        []
    ))

    # Save TXT and CSV reports.
    reports_dir = ML_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    txt_path = reports_dir / "aml_edge_case_results.txt"
    csv_path = reports_dir / "aml_edge_case_results.csv"

    with txt_path.open("w", encoding="utf-8") as report:
        report.write("=" * 78 + "\n")
        report.write("FINSHIELD AI - AML EDGE-CASE TEST RESULTS\n")
        report.write("=" * 78 + "\n")
        report.write("Tests: 16 to 25 (10 additional scenarios)\n")
        report.write("PASS = test behaved as expected; REVIEW = inspect validation/logic; "
                     "FAIL = valid-input test failed.\n\n")

        for item in results:
            report.write("-" * 78 + "\n")
            report.write(item["name"] + "\n")
            report.write("Status: " + item["status"] + "\n")
            report.write("Details: " + item["details"] + "\n")

            result = item.get("result")
            if result:
                report.write("AML score: " + str(result.get("aml_score")) + "\n")
                report.write("Risk level: " + str(result.get("risk_level")) + "\n")
                report.write("Rule score: " + str(result.get("rule_score")) + "\n")
                report.write("Behaviour score: " + str(result.get("behavior_score")) + "\n")
                report.write("Network score: " + str(result.get("network_score")) + "\n")
                report.write("Triggered rules: " +
                             json.dumps(result.get("triggered_rules", [])) + "\n")
                report.write("Reasons: " +
                             json.dumps(result.get("reasons", [])) + "\n")
                report.write("Notification: " +
                             json.dumps(result.get("notification", {}), default=str) + "\n")
            report.write("\n")

        passed = sum(x["status"] == "PASS" for x in results)
        reviewed = sum(x["status"] == "REVIEW" for x in results)
        failed = sum(x["status"] == "FAIL" for x in results)

        report.write("=" * 78 + "\n")
        report.write("SUMMARY\n")
        report.write("=" * 78 + "\n")
        report.write(f"Total tests: {len(results)}\n")
        report.write(f"PASS: {passed}\n")
        report.write(f"REVIEW: {reviewed}\n")
        report.write(f"FAIL: {failed}\n")
        report.write(f"TXT report: {txt_path}\n")
        report.write(f"CSV report: {csv_path}\n")

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["test", "status", "details", "aml_score", "risk_level",
                        "rule_score", "behavior_score", "network_score",
                        "triggered_rules"]
        )
        writer.writeheader()
        for item in results:
            result = item.get("result") or {}
            writer.writerow({
                "test": item["name"],
                "status": item["status"],
                "details": item["details"],
                "aml_score": result.get("aml_score", ""),
                "risk_level": result.get("risk_level", ""),
                "rule_score": result.get("rule_score", ""),
                "behavior_score": result.get("behavior_score", ""),
                "network_score": result.get("network_score", ""),
                "triggered_rules": json.dumps(result.get("triggered_rules", []))
            })

    print("\n".join(
        f'{x["name"]}: {x["status"]} - {x["details"]}' for x in results
    ))
    print("\nSUMMARY")
    print(f"Total: {len(results)} | PASS: {passed} | REVIEW: {reviewed} | FAIL: {failed}")
    print(f"TXT report saved to: {txt_path}")
    print(f"CSV report saved to: {csv_path}")


if __name__ == "__main__":
    main()
