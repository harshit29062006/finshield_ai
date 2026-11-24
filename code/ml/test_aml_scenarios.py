
import sys
import json
import csv
from pathlib import Path

# ------------------------------------------------------------
# FINSHIELD AI - COMPREHENSIVE AML TESTING
# 17 UNIQUE SCENARIOS
# ------------------------------------------------------------

ML_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ML_DIR))

from src.analysis_aml import analyze_aml
from src.explanation_aml import generate_detailed_aml_explanation


TIMESTAMP = "2026/10/29 10:00"


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def create_transaction(
    sender,
    receiver,
    amount,
    timestamp=TIMESTAMP,
    payment_type="TRANSFER"
):
    """Create a transaction in the format expected by AML modules."""

    return {
        "timestamp": timestamp,
        "sender_id": sender,
        "sender_account": sender,
        "receiver_id": receiver,
        "receiver_account": receiver,
        "amount": float(amount),
        "currency": "USD",
        "payment_type": payment_type
    }


def make_history(sender, entries):
    """
    Create transaction history.

    entries format:
    [(receiver, amount, timestamp), ...]
    """

    return [
        create_transaction(sender, receiver, amount, timestamp)
        for receiver, amount, timestamp in entries
    ]


def scenario(name, transaction, history, purpose):
    return {
        "name": name,
        "transaction": transaction,
        "history": history,
        "purpose": purpose
    }


def safe_json(value):
    return json.dumps(
        value,
        indent=4,
        ensure_ascii=False,
        default=str
    )


# ------------------------------------------------------------
# 17 AML TEST SCENARIOS
# ------------------------------------------------------------

scenarios = [

    # 1. Normal transaction
    scenario(
        "01 - Normal low-value transaction",
        create_transaction("S01", "R01", 500),
        [],
        "Baseline test with no suspicious indicators."
    ),

    # 2. High-value threshold boundary: below 100,000
    scenario(
        "02 - Amount just below high-value threshold",
        create_transaction("S02", "R02", 99999),
        [],
        "Checks whether HIGH_AMOUNT stays inactive below 100,000."
    ),

    # 3. High-value threshold boundary: 100,000
    scenario(
        "03 - Amount at high-value threshold",
        create_transaction("S03", "R03", 100000),
        [],
        "Checks the HIGH_AMOUNT threshold at 100,000."
    ),

    # 4. New receiver below 50,000
    scenario(
        "04 - New receiver below large-transfer threshold",
        create_transaction("S04", "R04_NEW", 49999),
        make_history("S04", [
            ("R04_OLD1", 1000, "2026/10/29 08:00"),
            ("R04_OLD2", 1200, "2026/10/29 09:00")
        ]),
        "Checks the new-receiver amount threshold below 50,000."
    ),

    # 5. New receiver with a large transaction
    scenario(
        "05 - Large transfer to a new receiver",
        create_transaction("S05", "R05_NEW", 60000),
        make_history("S05", [
            ("R05_OLD1", 1000, "2026/10/29 08:00"),
            ("R05_OLD2", 2000, "2026/10/29 09:00")
        ]),
        "Checks NEW_RECEIVER_LARGE_AMOUNT and unusual amount behaviour."
    ),

    # 6. Four transactions including current transaction
    scenario(
        "06 - Four transactions in 24 hours",
        create_transaction("S06", "R06", 1000),
        make_history("S06", [
            ("R06", 900, "2026/10/29 09:10"),
            ("R06", 850, "2026/10/29 09:20"),
            ("R06", 800, "2026/10/29 09:30")
        ]),
        "Checks frequency when four transactions exist including current."
    ),

    # 7. Five transactions including current transaction
    scenario(
        "07 - Five transactions in 24 hours",
        create_transaction("S07", "R07", 1000),
        make_history("S07", [
            ("R07", 900, "2026/10/29 09:10"),
            ("R07", 850, "2026/10/29 09:20"),
            ("R07", 800, "2026/10/29 09:30"),
            ("R07", 750, "2026/10/29 09:40")
        ]),
        "Checks HIGH_FREQUENCY at five transactions including current."
    ),

    # 8. Behaviour ratio around 2x
    scenario(
        "08 - Behaviour ratio around 2x",
        create_transaction("S08", "R08_NEW", 2000),
        make_history("S08", [
            ("R08_A", 1000, "2026/10/29 08:00"),
            ("R08_B", 1000, "2026/10/29 09:00")
        ]),
        "Checks behaviour scoring around the 2x historical-average boundary."
    ),

    # 9. Behaviour ratio around 3x
    scenario(
        "09 - Behaviour ratio around 3x",
        create_transaction("S09", "R09_NEW", 3000),
        make_history("S09", [
            ("R09_A", 1000, "2026/10/29 08:00"),
            ("R09_B", 1000, "2026/10/29 09:00")
        ]),
        "Checks behaviour scoring around the 3x historical-average boundary."
    ),

    # 10. Behaviour ratio around 5x
    scenario(
        "10 - Behaviour ratio around 5x",
        create_transaction("S10", "R10_NEW", 5000),
        make_history("S10", [
            ("R10_A", 1000, "2026/10/29 08:00"),
            ("R10_B", 1000, "2026/10/29 09:00")
        ]),
        "Checks behaviour scoring around the 5x historical-average boundary."
    ),

    # 11. Multiple receivers
    scenario(
        "11 - Sender connected to multiple receivers",
        create_transaction("S11", "R11_NEW", 2000),
        make_history("S11", [
            ("R11_A", 1000, "2026/10/29 08:10"),
            ("R11_B", 1100, "2026/10/29 08:20"),
            ("R11_C", 1200, "2026/10/29 08:30"),
            ("R11_D", 1300, "2026/10/29 08:40"),
            ("R11_E", 1400, "2026/10/29 08:50")
        ]),
        "Checks network risk from a sender connected to many receivers."
    ),

    # 12. Multiple senders connected to one receiver
    scenario(
        "12 - Receiver connected to multiple senders",
        create_transaction("S12", "R12", 2000),
        [
            create_transaction("S12_A", "R12", 1000, "2026/10/29 08:10"),
            create_transaction("S12_B", "R12", 1100, "2026/10/29 08:20"),
            create_transaction("S12_C", "R12", 1200, "2026/10/29 08:30"),
            create_transaction("S12_D", "R12", 1300, "2026/10/29 08:40"),
            create_transaction("S12_E", "R12", 1400, "2026/10/29 08:50")
        ],
        "Checks network risk from many incoming transfers to one receiver."
    ),

    # 13. Reciprocal transactions
    scenario(
        "13 - Reciprocal transaction relationship",
        create_transaction("S13", "R13", 5000),
        [
            create_transaction("R13", "S13", 4500, "2026/10/29 09:30")
        ],
        "Checks reciprocal sender-receiver relationship detection."
    ),

    # 14. Multiple suspicious indicators
    scenario(
        "14 - Combined high-risk indicators",
        create_transaction("S14", "R14_NEW", 150000),
        make_history("S14", [
            ("R14_A", 1000, "2026/10/29 08:10"),
            ("R14_B", 1000, "2026/10/29 08:20"),
            ("R14_C", 1000, "2026/10/29 08:30"),
            ("R14_D", 1000, "2026/10/29 08:40"),
            ("R14_E", 1000, "2026/10/29 08:50")
        ]),
        "Combines high amount, new receiver, frequency and unusual behaviour."
    ),

    # 15. Stable customer activity
    scenario(
        "15 - Stable customer activity",
        create_transaction("S15", "R15", 1000),
        make_history("S15", [
            ("R15", 950, "2026/10/28 10:00"),
            ("R15", 1050, "2026/10/28 12:00"),
            ("R15", 1000, "2026/10/28 14:00"),
            ("R15", 980, "2026/10/28 16:00"),
            ("R15", 1020, "2026/10/28 18:00"),
            ("R15", 990, "2026/10/28 20:00"),
            ("R15", 1010, "2026/10/28 22:00"),
            ("R15", 1000, "2026/10/29 00:00"),
            ("R15", 970, "2026/10/29 02:00"),
            ("R15", 1030, "2026/10/29 04:00")
        ]),
        "Checks whether consistent historical activity receives a low score."
    ),

    # 16. Your original standalone high-value transaction
    scenario(
        "16 - Standalone high-value transaction",
        create_transaction("S16", "R16", 150000),
        [],
        "Tests a 150,000 high-value transaction without other suspicious indicators."
    ),

    # 17. Your original repeated transaction scenario
    # Five historical + one current = six transactions
    scenario(
        "17 - Six repeated transactions in 24 hours",
        create_transaction("S17", "R17", 1000),
        make_history("S17", [
            ("R17", 900, "2026/10/29 09:10"),
            ("R17", 850, "2026/10/29 09:20"),
            ("R17", 800, "2026/10/29 09:30"),
            ("R17", 750, "2026/10/29 09:40"),
            ("R17", 700, "2026/10/29 09:50")
        ]),
        "Checks HIGH_FREQUENCY with six transactions including current."
    )
]


# ------------------------------------------------------------
# RUN AML ANALYSIS AND GENERATE REPORTS
# ------------------------------------------------------------

def run_tests():

    reports_dir = ML_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    csv_path = reports_dir / "aml_scenario_results.csv"
    txt_path = reports_dir / "aml_scenario_results.txt"

    rows = []
    passed = 0
    failed = 0

    with txt_path.open("w", encoding="utf-8") as report:

        def output(message=""):
            print(message)
            report.write(str(message) + "\n")

        output("=" * 78)
        output("FINSHIELD AI - AML COMPREHENSIVE SCENARIO TESTING")
        output("=" * 78)

        output(f"Total scenarios: {len(scenarios)}")
        output("AML score formula: 45% rule + 35% behaviour + 20% network")
        output("Risk thresholds: LOW < 0.40 | MEDIUM 0.40-0.6999 | HIGH >= 0.70")

        for item in scenarios:

            transaction = item["transaction"]
            history = item["history"]

            output("\n" + "-" * 78)
            output(item["name"])
            output("-" * 78)

            output("Purpose: " + item["purpose"])
            output("Sender: " + str(transaction["sender_id"]))
            output("Receiver: " + str(transaction["receiver_id"]))
            output("Amount: " + f'{transaction["amount"]:,.2f} USD')
            output("Timestamp: " + str(transaction["timestamp"]))
            output("Payment type: " + str(transaction["payment_type"]))
            output("Historical transaction count: " + str(len(history)))

            try:

                # Run AML analysis
                result = analyze_aml(transaction, history)

                # Generate detailed explanation
                explanation_result = generate_detailed_aml_explanation(
                    transaction_data=transaction,
                    transaction_history=history,
                    analysis_result=result
                )

                # Handle explanation returned as dictionary or text
                if isinstance(explanation_result, dict):

                    detailed_text = explanation_result.get(
                        "explanation",
                        safe_json(explanation_result)
                    )

                else:
                    detailed_text = str(explanation_result)

                notification = result.get("notification", {})
                investigation = result.get("investigation_summary", "")

                aml_score = result.get("aml_score")

                output("\n--- AML COMPONENT SCORES ---")
                output("Rule score: " + str(result.get("rule_score")))
                output("Behaviour score: " + str(result.get("behavior_score")))
                output("Network score: " + str(result.get("network_score")))
                output("Final AML score: " + str(aml_score))

                if aml_score is not None:
                    output(
                        "Final AML percentage: "
                        + f"{float(aml_score) * 100:.2f}%"
                    )

                output("Risk level: " + str(result.get("risk_level")))

                output("\n--- TRIGGERED RULES ---")
                output(safe_json(result.get("triggered_rules", [])))

                output("\n--- REASONS ---")
                output(safe_json(result.get("reasons", [])))

                output("\n--- NOTIFICATION ---")
                output(safe_json(notification))

                output("\n--- INVESTIGATION SUMMARY ---")
                output(str(investigation))

                output("\n--- DETAILED AML EXPLANATION ---")
                output(detailed_text)

                # Successful execution of both analysis functions
                output("\nTEST RESULT: PASS")
                passed += 1

                rows.append({
                    "scenario": item["name"],
                    "sender": transaction["sender_id"],
                    "receiver": transaction["receiver_id"],
                    "amount": transaction["amount"],
                    "history_count": len(history),
                    "rule_score": result.get("rule_score"),
                    "behavior_score": result.get("behavior_score"),
                    "network_score": result.get("network_score"),
                    "aml_score": aml_score,
                    "aml_percentage": (
                        round(float(aml_score) * 100, 2)
                        if aml_score is not None else ""
                    ),
                    "risk_level": result.get("risk_level"),
                    "triggered_rules": safe_json(
                        result.get("triggered_rules", [])
                    ),
                    "notification": safe_json(notification),
                    "test_status": "PASS",
                    "error": ""
                })

            except Exception as exc:

                output("\nTEST RESULT: FAIL")
                output("Error: " + str(exc))

                failed += 1

                rows.append({
                    "scenario": item["name"],
                    "sender": transaction["sender_id"],
                    "receiver": transaction["receiver_id"],
                    "amount": transaction["amount"],
                    "history_count": len(history),
                    "rule_score": "",
                    "behavior_score": "",
                    "network_score": "",
                    "aml_score": "",
                    "aml_percentage": "",
                    "risk_level": "",
                    "triggered_rules": "",
                    "notification": "",
                    "test_status": "FAIL",
                    "error": str(exc)
                })

        # Final testing summary
        output("\n" + "=" * 78)
        output("AML TESTING SUMMARY")
        output("=" * 78)

        output(f"Total scenarios: {len(scenarios)}")
        output(f"Passed: {passed}")
        output(f"Failed: {failed}")

        output(f"CSV report: {csv_path}")
        output(f"Text report: {txt_path}")

        output("=" * 78)

    # Save CSV report
    fieldnames = [
        "scenario",
        "sender",
        "receiver",
        "amount",
        "history_count",
        "rule_score",
        "behavior_score",
        "network_score",
        "aml_score",
        "aml_percentage",
        "risk_level",
        "triggered_rules",
        "notification",
        "test_status",
        "error"
    ]

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\nReports saved successfully.")

    return passed, failed


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

if __name__ == "__main__":
    run_tests()
