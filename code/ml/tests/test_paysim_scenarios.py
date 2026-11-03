import os
import sys
import pandas as pd

# Allow importing the existing backend ML service
sys.path.insert(0, os.path.abspath("backend"))

from app.services.ml_service import ml_service, build_features


# ============================================================
# 1. TEN PAYSim TEST SCENARIOS
# ============================================================

TEST_CASES = [

    {
        "case_id": "PAY_01",
        "scenario": "Normal small payment",
        "expected": "LOW",
        "transaction": {
            "step": 100,
            "type": "PAYMENT",
            "amount": 500,
            "oldbalanceOrg": 10000,
            "newbalanceOrig": 9500,
            "oldbalanceDest": 5000,
            "newbalanceDest": 5500,
            "isFlaggedFraud": 0
        }
    },

    {
        "case_id": "PAY_02",
        "scenario": "Normal cash withdrawal",
        "expected": "LOW",
        "transaction": {
            "step": 120,
            "type": "CASH_OUT",
            "amount": 2000,
            "oldbalanceOrg": 15000,
            "newbalanceOrig": 13000,
            "oldbalanceDest": 0,
            "newbalanceDest": 0,
            "isFlaggedFraud": 0
        }
    },

    {
        "case_id": "PAY_03",
        "scenario": "Normal money transfer",
        "expected": "LOW",
        "transaction": {
            "step": 150,
            "type": "TRANSFER",
            "amount": 5000,
            "oldbalanceOrg": 20000,
            "newbalanceOrig": 15000,
            "oldbalanceDest": 10000,
            "newbalanceDest": 15000,
            "isFlaggedFraud": 0
        }
    },

    {
        "case_id": "PAY_04",
        "scenario": "Normal cash deposit",
        "expected": "LOW",
        "transaction": {
            "step": 180,
            "type": "CASH_IN",
            "amount": 3000,
            "oldbalanceOrg": 5000,
            "newbalanceOrig": 8000,
            "oldbalanceDest": 10000,
            "newbalanceDest": 7000,
            "isFlaggedFraud": 0
        }
    },

    {
        "case_id": "PAY_05",
        "scenario": "Large transfer with sufficient balance",
        "expected": "REVIEW",
        "transaction": {
            "step": 250,
            "type": "TRANSFER",
            "amount": 75000,
            "oldbalanceOrg": 100000,
            "newbalanceOrig": 25000,
            "oldbalanceDest": 50000,
            "newbalanceDest": 125000,
            "isFlaggedFraud": 0
        }
    },

    {
        "case_id": "PAY_06",
        "scenario": "Large cash withdrawal",
        "expected": "REVIEW",
        "transaction": {
            "step": 300,
            "type": "CASH_OUT",
            "amount": 90000,
            "oldbalanceOrg": 100000,
            "newbalanceOrig": 10000,
            "oldbalanceDest": 0,
            "newbalanceDest": 0,
            "isFlaggedFraud": 0
        }
    },

    {
        "case_id": "PAY_07",
        "scenario": "Entire sender balance transferred",
        "expected": "HIGH",
        "transaction": {
            "step": 350,
            "type": "TRANSFER",
            "amount": 500000,
            "oldbalanceOrg": 500000,
            "newbalanceOrig": 0,
            "oldbalanceDest": 10000,
            "newbalanceDest": 510000,
            "isFlaggedFraud": 0
        }
    },

    {
        "case_id": "PAY_08",
        "scenario": "Large transfer with insufficient sender balance",
        "expected": "HIGH",
        "transaction": {
            "step": 400,
            "type": "TRANSFER",
            "amount": 900000,
            "oldbalanceOrg": 300000,
            "newbalanceOrig": 0,
            "oldbalanceDest": 10000,
            "newbalanceDest": 910000,
            "isFlaggedFraud": 0
        }
    },

    {
        "case_id": "PAY_09",
        "scenario": "Flagged large transfer",
        "expected": "HIGH",
        "transaction": {
            "step": 450,
            "type": "TRANSFER",
            "amount": 200000,
            "oldbalanceOrg": 200000,
            "newbalanceOrig": 0,
            "oldbalanceDest": 5000,
            "newbalanceDest": 205000,
            "isFlaggedFraud": 1
        }
    },

    {
        "case_id": "PAY_10",
        "scenario": "Very large account-draining transfer",
        "expected": "HIGH",
        "transaction": {
            "step": 500,
            "type": "TRANSFER",
            "amount": 900000,
            "oldbalanceOrg": 900000,
            "newbalanceOrig": 0,
            "oldbalanceDest": 10000,
            "newbalanceDest": 910000,
            "isFlaggedFraud": 0
        }
    }
]


# ============================================================
# 2. MODEL PREDICTION HELPER
# ============================================================

def extract_prediction(result):
    """
    Supports the prediction dictionary returned by MLService.
    """
    if isinstance(result, dict):
        score = result.get("fraud_score")
        prediction = result.get("prediction")

        if score is None:
            raise ValueError(f"fraud_score missing from result: {result}")

        if prediction is None:
            prediction = int(float(score) >= 0.5)

        return float(score), int(prediction)

    raise TypeError(f"Unexpected prediction result: {result}")


# ============================================================
# 3. RUN TESTS
# ============================================================

def main():

    print("\n" + "=" * 75)
    print("                 PAYSim MODEL VALIDATION")
    print("=" * 75)

    print("\nService ready:", ml_service.is_ready)
    print("Available models:", ml_service.available_models())
    print("Load error:", ml_service.load_error)

    model_names = [
        "logistic_regression",
        "random_forest",
        "xgboost"
    ]

    missing = [
        name for name in model_names
        if name not in ml_service.models
    ]

    if missing:
        print("\nERROR: These models could not be loaded:", missing)
        print("Please check the model files and dependencies.")
        return

    results = []

    for case in TEST_CASES:

        transaction = case["transaction"]

        print("\n" + "-" * 75)
        print(case["case_id"], "-", case["scenario"])
        print("-" * 75)

        print("\nTRANSACTION DETAILS")

        for key, value in transaction.items():
            print(f"{key:22s}: {value}")

        features = build_features(transaction)

        print("\nENGINEERED FEATURES")
        print(features.to_string(index=False))

        row = {
            "case_id": case["case_id"],
            "scenario": case["scenario"],
            "expected": case["expected"],
            **transaction
        }

        print("\nMODEL PREDICTIONS")

        for model_name in model_names:

            try:
                prediction_result = ml_service.predict(
                    transaction,
                    model_name
                )

                score, prediction = extract_prediction(
                    prediction_result
                )

                result_label = (
                    "FRAUD" if prediction == 1 else "NON-FRAUD"
                )

                print(f"\n{model_name.upper()}")
                print(f"Fraud probability : {score:.6f}")
                print(f"Fraud percentage  : {score * 100:.2f}%")
                print(f"Prediction        : {prediction} ({result_label})")

                row[f"{model_name}_fraud_score"] = score
                row[f"{model_name}_fraud_percentage"] = score * 100
                row[f"{model_name}_prediction"] = prediction

            except Exception as error:
                print(f"\nERROR in {model_name}: {error}")
                row[f"{model_name}_fraud_score"] = None
                row[f"{model_name}_fraud_percentage"] = None
                row[f"{model_name}_prediction"] = None

        results.append(row)

    # ========================================================
    # 4. SAVE CSV REPORT
    # ========================================================

    os.makedirs("ml/reports", exist_ok=True)

    output_file = "ml/reports/paysim_scenario_results.csv"

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)

    print("\n" + "=" * 75)
    print("                 FINAL SUMMARY")
    print("=" * 75)

    summary_columns = [
        "case_id",
        "scenario",
        "expected",
        "logistic_regression_fraud_score",
        "logistic_regression_prediction",
        "random_forest_fraud_score",
        "random_forest_prediction",
        "xgboost_fraud_score",
        "xgboost_prediction"
    ]

    print(results_df[summary_columns].to_string(index=False))

    print("\nDetailed report saved to:", output_file)
    print("\nPaySim scenario testing completed.")


if __name__ == "__main__":
    main()
