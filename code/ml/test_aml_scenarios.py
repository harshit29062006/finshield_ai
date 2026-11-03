
# import sys
# import json
# from pathlib import Path

# # Add the ML directory to Python's import path
# ML_DIR = Path(__file__).resolve().parent
# sys.path.insert(0, str(ML_DIR))

# from src.analysis_aml import analyze_aml
# from src.explanation_aml import generate_detailed_aml_explanation


# # --------------------------------------------------
# # Helper function to create transactions
# # --------------------------------------------------

# def create_transaction(
#     sender,
#     receiver,
#     amount,
#     timestamp="2026/10/29 10:00",
#     payment_type="TRANSFER"
# ):
#     return {
#         "timestamp": timestamp,
#         "sender_id": sender,
#         "sender_account": sender,
#         "receiver_id": receiver,
#         "receiver_account": receiver,
#         "amount": amount,
#         "currency": "USD",
#         "payment_type": payment_type
#     }


# # --------------------------------------------------
# # Test scenarios
# # --------------------------------------------------

# scenarios = [

#     {
#         "name": "Scenario 1: Normal Transaction",
#         "transaction": create_transaction(
#             "S1", "R1", 500
#         ),
#         "history": []
#     },

#     {
#         "name": "Scenario 2: High-Value Transaction",
#         "transaction": create_transaction(
#             "S2", "R2", 150000
#         ),
#         "history": []
#     },

#     {
#         "name": "Scenario 3: New Receiver",
#         "transaction": create_transaction(
#             "S3", "R_NEW", 60000
#         ),
#         "history": [
#             create_transaction(
#                 "S3", "R_OLD1", 1000,
#                 "2026/10/29 08:00"
#             ),
#             create_transaction(
#                 "S3", "R_OLD2", 2000,
#                 "2026/10/29 09:00"
#             )
#         ]
#     },

#     {
#         "name": "Scenario 4: Repeated Transactions",
#         "transaction": create_transaction(
#             "S4", "R4", 1000,
#             "2026/10/29 10:00"
#         ),
#         "history": [
#             create_transaction(
#                 "S4", "R4", 900,
#                 "2026/10/29 09:50"
#             ),
#             create_transaction(
#                 "S4", "R4", 800,
#                 "2026/10/29 09:40"
#             ),
#             create_transaction(
#                 "S4", "R4", 700,
#                 "2026/10/29 09:30"
#             ),
#             create_transaction(
#                 "S4", "R4", 600,
#                 "2026/10/29 09:20"
#             ),
#             create_transaction(
#                 "S4", "R4", 500,
#                 "2026/10/29 09:10"
#             )
#         ]
#     },

#     {
#         "name": "Scenario 5: Multiple Receivers",
#         "transaction": create_transaction(
#             "S5", "R_NEW5", 2000,
#             "2026/10/29 10:00"
#         ),
#         "history": [
#             create_transaction(
#                 "S5", "R10", 1000,
#                 "2026/10/29 09:50"
#             ),
#             create_transaction(
#                 "S5", "R11", 1200,
#                 "2026/10/29 09:40"
#             ),
#             create_transaction(
#                 "S5", "R12", 1500,
#                 "2026/10/29 09:30"
#             ),
#             create_transaction(
#                 "S5", "R13", 1800,
#                 "2026/10/29 09:20"
#             ),
#             create_transaction(
#                 "S5", "R14", 2000,
#                 "2026/10/29 09:10"
#             )
#         ]
#     },

#     {
#         "name": "Scenario 6: Reciprocal Transactions",
#         "transaction": create_transaction(
#             "S6", "R6", 5000,
#             "2026/10/29 10:00"
#         ),
#         "history": [
#             create_transaction(
#                 "R6", "S6", 4500,
#                 "2026/10/29 09:30"
#             )
#         ]
#     }
# ]


# # --------------------------------------------------
# # Run AML analysis and explanation
# # --------------------------------------------------

# def run_tests():

#     print("\n" + "=" * 65)
#     print("FINSHIELD AI - AML SCENARIO TESTING")
#     print("=" * 65)

#     for scenario in scenarios:

#         name = scenario["name"]
#         transaction = scenario["transaction"]
#         history = scenario["history"]

#         print("\n" + "-" * 65)
#         print(name)
#         print("-" * 65)

#         try:

#             # Run AML analysis
#             result = analyze_aml(transaction, history)

#             # Generate detailed explanation
#             explanation = generate_detailed_aml_explanation(
#                 transaction_data=transaction,
#                 transaction_history=history,
#                 analysis_result=result
#             )

#             # Display transaction information
#             print("Sender:", transaction["sender_id"])
#             print("Receiver:", transaction["receiver_id"])
#             print("Amount:", transaction["amount"])
#             print("History size:", len(history))

#             # Display AML results
#             print("\nAML Score:", result.get("aml_score"))
#             print("Risk Level:", result.get("risk_level"))
#             print("Rule Score:", result.get("rule_score"))
#             print("Behavior Score:", result.get("behavior_score"))
#             print("Network Score:", result.get("network_score"))

#             print("\nTriggered Rules:")
#             print(json.dumps(
#                 result.get("triggered_rules", []),
#                 indent=4,
#                 default=str
#             ))

#             print("\nReasons:")
#             print(json.dumps(
#                 result.get("reasons", []),
#                 indent=4,
#                 default=str
#             ))

#             print("\nDetailed Explanation:")
#             print(explanation)

#             print("\nTEST RESULT: PASS")

#         except Exception as e:

#             print("\nTEST RESULT: FAIL")
#             print("Error:", str(e))

#     print("\n" + "=" * 65)
#     print("AML SCENARIO TESTING COMPLETED")
#     print("=" * 65)


# if __name__ == "__main__":
#     run_tests()

import sys
import json
import csv
from pathlib import Path

# ------------------------------------------------------------
# FINSHIELD AI - AML TESTING (15 DETAILED SCENARIOS)
# ------------------------------------------------------------

ML_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ML_DIR))

from src.analysis_aml import analyze_aml
from src.explanation_aml import generate_detailed_aml_explanation


TIMESTAMP = "2026/10/29 10:00"


def create_transaction(
    sender,
    receiver,
    amount,
    timestamp=TIMESTAMP,
    payment_type="TRANSFER"
):
    """Create one transaction in the format expected by the AML modules."""
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


# Keep timestamps within 24 hours for frequency tests.
scenarios = [

    # 1. Ordinary transaction, no prior history.
    scenario(
        "01 - Normal low-value transaction",
        create_transaction("S01", "R01", 500),
        [],
        "Baseline test with no suspicious indicators."
    ),

    # 2. High amount threshold: below 100,000.
    scenario(
        "02 - Amount just below high-value threshold",
        create_transaction("S02", "R02", 99999),
        [],
        "Checks whether HIGH_AMOUNT stays inactive below 100,000."
    ),

    # 3. High amount threshold: at/above 100,000.
    scenario(
        "03 - Amount at high-value threshold",
        create_transaction("S03", "R03", 100000),
        [],
        "Checks the HIGH_AMOUNT threshold at 100,000."
    ),

    # 4. New receiver threshold below 50,000.
    scenario(
        "04 - New receiver below large-transfer threshold",
        create_transaction("S04", "R04_NEW", 49999),
        make_history("S04", [
            ("R04_OLD1", 1000, "2026/10/29 08:00"),
            ("R04_OLD2", 1200, "2026/10/29 09:00")
        ]),
        "Checks the new-receiver amount threshold below 50,000."
    ),

    # 5. New receiver at threshold, and amount is a large jump.
    scenario(
        "05 - Large transfer to a new receiver",
        create_transaction("S05", "R05_NEW", 60000),
        make_history("S05", [
            ("R05_OLD1", 1000, "2026/10/29 08:00"),
            ("R05_OLD2", 2000, "2026/10/29 09:00")
        ]),
        "Checks NEW_RECEIVER_LARGE_AMOUNT and unusual amount behaviour."
    ),

    # 6. Four transactions including current: should be below 5 count.
    scenario(
        "06 - Four transactions in 24 hours",
        create_transaction("S06", "R06", 1000),
        make_history("S06", [
            ("R06", 900, "2026/10/29 09:10"),
            ("R06", 850, "2026/10/29 09:20"),
            ("R06", 800, "2026/10/29 09:30")
        ]),
        "Checks frequency when only four transactions exist including current."
    ),

    # 7. Five transactions including current: high frequency should trigger.
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

    # 8. Current amount is 2x average; behaviour boundary.
    scenario(
        "08 - Behaviour ratio around 2x",
        create_transaction("S08", "R08_NEW", 2000),
        make_history("S08", [
            ("R08_A", 1000, "2026/10/29 08:00"),
            ("R08_B", 1000, "2026/10/29 09:00")
        ]),
        "Checks behaviour scoring around the 2x historical-average boundary."
    ),

    # 9. Current amount is 3x average.
    scenario(
        "09 - Behaviour ratio around 3x",
        create_transaction("S09", "R09_NEW", 3000),
        make_history("S09", [
            ("R09_A", 1000, "2026/10/29 08:00"),
            ("R09_B", 1000, "2026/10/29 09:00")
        ]),
        "Checks behaviour scoring around the 3x historical-average boundary."
    ),

    # 10. Current amount is 5x average.
    scenario(
        "10 - Behaviour ratio around 5x",
        create_transaction("S10", "R10_NEW", 5000),
        make_history("S10", [
            ("R10_A", 1000, "2026/10/29 08:00"),
            ("R10_B", 1000, "2026/10/29 09:00")
        ]),
        "Checks behaviour scoring around the 5x historical-average boundary."
    ),

    # 11. Sender has many different receivers.
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

    # 12. Receiver has multiple incoming transactions.
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

    # 13. Reciprocal transaction: receiver previously sent money to sender.
    scenario(
        "13 - Reciprocal transaction relationship",
        create_transaction("S13", "R13", 5000),
        [
            create_transaction("R13", "S13", 4500, "2026/10/29 09:30")
        ],
        "Checks reciprocal sender-receiver relationship detection."
    ),

    # 14. Multiple suspicious signals at once.
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
        "Combines high amount, new receiver, frequency, and unusual behaviour."
    ),

    # 15. Ordinary transaction with a long stable history.
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
    )
]


def safe_json(value):
    return json.dumps(value, indent=4, ensure_ascii=False, default=str)


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
                result = analyze_aml(transaction, history)

                explanation_result = generate_detailed_aml_explanation(
                    transaction_data=transaction,
                    transaction_history=history,
                    analysis_result=result
                )

                # The explanation function in this project returns a dictionary.
                if isinstance(explanation_result, dict):
                    detailed_text = explanation_result.get(
                        "explanation", safe_json(explanation_result)
                    )
                    transaction_id = explanation_result.get("transaction_id")
                else:
                    detailed_text = str(explanation_result)
                    transaction_id = None

                notification = result.get("notification", {})
                investigation = result.get("investigation_summary", "")

                output("\n--- AML COMPONENT SCORES ---")
                output("Rule score: " + str(result.get("rule_score")))
                output("Behaviour score: " + str(result.get("behavior_score")))
                output("Network score: " + str(result.get("network_score")))
                output("Final AML score: " + str(result.get("aml_score")))
                output("Final AML percentage: " +
                       f'{float(result.get("aml_score", 0)) * 100:.2f}%')
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
                    "aml_score": result.get("aml_score"),
                    "aml_percentage": round(float(result.get("aml_score", 0)) * 100, 2),
                    "risk_level": result.get("risk_level"),
                    "triggered_rules": "; ".join(result.get("triggered_rules", [])),
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

        output("\n" + "=" * 78)
        output("AML TESTING SUMMARY")
        output("=" * 78)
        output(f"Total scenarios: {len(scenarios)}")
        output(f"Passed: {passed}")
        output(f"Failed: {failed}")
        output(f"CSV report: {csv_path}")
        output(f"Text report: {txt_path}")
        output("=" * 78)

    fieldnames = [
        "scenario", "sender", "receiver", "amount", "history_count",
        "rule_score", "behavior_score", "network_score", "aml_score",
        "aml_percentage", "risk_level", "triggered_rules",
        "notification", "test_status", "error"
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\nReports saved successfully.")


if __name__ == "__main__":
    run_tests()
