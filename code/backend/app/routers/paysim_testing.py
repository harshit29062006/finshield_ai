
# """Admin-only PaySim model testing endpoint.

# Runs 10 synthetic PaySim scenarios through all available ML models.
# No transaction or risk-result records are saved to the database.
# """

# from fastapi import APIRouter, Depends

# from app.deps import require_roles
# from app.models import ROLE_ADMIN
# from app.services.ml_service import ml_service, build_features

# router = APIRouter(
#     prefix="/api/admin/paysim-testing",
#     tags=["PaySim Testing"],
#     dependencies=[Depends(require_roles(ROLE_ADMIN))],
# )

# MODEL_NAMES = [
#     "logistic_regression",
#     "random_forest",
#     "xgboost",
# ]

# TEST_CASES = [
#     {
#         "id": "PAY_01",
#         "name": "Normal small payment",
#         "description": "An ordinary low-value payment with consistent balances.",
#         "expected_category": "LOW",
#         "transaction": {
#             "step": 100, "type": "PAYMENT", "amount": 500,
#             "oldbalanceOrg": 10000, "newbalanceOrig": 9500,
#             "oldbalanceDest": 5000, "newbalanceDest": 5500,
#             "isFlaggedFraud": 0,
#         },
#     },
#     {
#         "id": "PAY_02",
#         "name": "Normal cash withdrawal",
#         "description": "A regular cash withdrawal with sufficient sender balance.",
#         "expected_category": "LOW",
#         "transaction": {
#             "step": 120, "type": "CASH_OUT", "amount": 2000,
#             "oldbalanceOrg": 15000, "newbalanceOrig": 13000,
#             "oldbalanceDest": 0, "newbalanceDest": 0,
#             "isFlaggedFraud": 0,
#         },
#     },
#     {
#         "id": "PAY_03",
#         "name": "Normal money transfer",
#         "description": "A regular transfer with consistent account balances.",
#         "expected_category": "LOW",
#         "transaction": {
#             "step": 150, "type": "TRANSFER", "amount": 5000,
#             "oldbalanceOrg": 20000, "newbalanceOrig": 15000,
#             "oldbalanceDest": 10000, "newbalanceDest": 15000,
#             "isFlaggedFraud": 0,
#         },
#     },
#     {
#         "id": "PAY_04",
#         "name": "Cash deposit",
#         "description": "Provisional CASH_IN scenario; destination balance pattern needs validation.",
#         "expected_category": "LOW (provisional)",
#         "transaction": {
#             "step": 180, "type": "CASH_IN", "amount": 3000,
#             "oldbalanceOrg": 5000, "newbalanceOrig": 8000,
#             "oldbalanceDest": 10000, "newbalanceDest": 7000,
#             "isFlaggedFraud": 0,
#         },
#     },
#     {
#         "id": "PAY_05",
#         "name": "Large transfer with sufficient balance",
#         "description": "A high-value transfer with consistent balances.",
#         "expected_category": "REVIEW",
#         "transaction": {
#             "step": 250, "type": "TRANSFER", "amount": 75000,
#             "oldbalanceOrg": 100000, "newbalanceOrig": 25000,
#             "oldbalanceDest": 50000, "newbalanceDest": 125000,
#             "isFlaggedFraud": 0,
#         },
#     },
#     {
#         "id": "PAY_06",
#         "name": "Large cash withdrawal",
#         "description": "A withdrawal using most of the sender's available balance.",
#         "expected_category": "REVIEW",
#         "transaction": {
#             "step": 300, "type": "CASH_OUT", "amount": 90000,
#             "oldbalanceOrg": 100000, "newbalanceOrig": 10000,
#             "oldbalanceDest": 0, "newbalanceDest": 0,
#             "isFlaggedFraud": 0,
#         },
#     },
#     {
#         "id": "PAY_07",
#         "name": "Entire sender balance transferred",
#         "description": "The transfer completely empties the sender's account.",
#         "expected_category": "HIGH",
#         "transaction": {
#             "step": 350, "type": "TRANSFER", "amount": 500000,
#             "oldbalanceOrg": 500000, "newbalanceOrig": 0,
#             "oldbalanceDest": 10000, "newbalanceDest": 510000,
#             "isFlaggedFraud": 0,
#         },
#     },
#     {
#         "id": "PAY_08",
#         "name": "Transfer exceeds sender balance",
#         "description": "An intentionally inconsistent synthetic balance scenario.",
#         "expected_category": "HIGH",
#         "transaction": {
#             "step": 400, "type": "TRANSFER", "amount": 900000,
#             "oldbalanceOrg": 300000, "newbalanceOrig": 0,
#             "oldbalanceDest": 10000, "newbalanceDest": 910000,
#             "isFlaggedFraud": 0,
#         },
#     },
#     {
#         "id": "PAY_09",
#         "name": "Flagged large transfer",
#         "description": "A large transfer with the PaySim fraud flag enabled.",
#         "expected_category": "HIGH",
#         "transaction": {
#             "step": 450, "type": "TRANSFER", "amount": 200000,
#             "oldbalanceOrg": 200000, "newbalanceOrig": 0,
#             "oldbalanceDest": 5000, "newbalanceDest": 205000,
#             "isFlaggedFraud": 1,
#         },
#     },
#     {
#         "id": "PAY_10",
#         "name": "Very large account-draining transfer",
#         "description": "An extremely large transfer that empties the sender's account.",
#         "expected_category": "HIGH",
#         "transaction": {
#             "step": 500, "type": "TRANSFER", "amount": 900000,
#             "oldbalanceOrg": 900000, "newbalanceOrig": 0,
#             "oldbalanceDest": 10000, "newbalanceDest": 910000,
#             "isFlaggedFraud": 0,
#         },
#     },
# ]


# def compare_with_expectation(expected_category, prediction):
#     """Compare binary ML output with LOW/HIGH expectations only."""
#     if expected_category.startswith("LOW"):
#         return "MATCH" if prediction == 0 else "DIFFERENT"

#     if expected_category == "HIGH":
#         return "MATCH" if prediction == 1 else "DIFFERENT"

#     return "MANUAL REVIEW - no direct binary comparison"


# @router.post("/run")
# def run_paysim_tests():
#     """Run all 10 synthetic scenarios through every available ML model."""

#     results = []

#     available_models = ml_service.available_models()

#     for case in TEST_CASES:
#         transaction = case["transaction"]
#         features = build_features(transaction)

#         model_results = {}

#         for model_name in MODEL_NAMES:
#             if model_name not in available_models:
#                 model_results[model_name] = {
#                     "available": False,
#                     "error": f"{model_name} is not loaded.",
#                 }
#                 continue

#             prediction_result = ml_service.predict(
#                 transaction,
#                 model_name=model_name,
#             )

#             if not prediction_result.get("available"):
#                 model_results[model_name] = prediction_result
#                 continue

#             probability = prediction_result["fraud_score"]
#             prediction = prediction_result["prediction"]

#             model_results[model_name] = {
#                 "available": True,
#                 "fraud_probability": probability,
#                 "fraud_probability_percent": round(probability * 100, 4),
#                 "prediction": prediction,
#                 "prediction_label": "FRAUD" if prediction == 1 else "NON-FRAUD",
#                 "expectation_result": compare_with_expectation(
#                     case["expected_category"],
#                     prediction,
#                 ),
#             }

#         results.append({
#             "id": case["id"],
#             "scenario": case["name"],
#             "description": case["description"],
#             "expected_category": case["expected_category"],
#             "transaction": transaction,
#             "engineered_features": features.to_dict(orient="records")[0],
#             "model_results": model_results,
#         })

#     return {
#         "message": "PaySim model testing completed.",
#         "scenarios_run": len(results),
#         "available_models": available_models,
#         "results": results,
#     }
"""Admin-only PaySim model testing endpoint.

Runs 10 synthetic PaySim scenarios through all available ML models.
No transaction or risk-result records are saved to the database.
"""

from fastapi import APIRouter, Depends

from app.deps import require_roles
from app.models import ROLE_ADMIN
from app.services.ml_service import build_features, ml_service

router = APIRouter(
    prefix="/api/admin/paysim-testing",
    tags=["PaySim Testing"],
    dependencies=[Depends(require_roles(ROLE_ADMIN))],
)

MODEL_NAMES = [
    "logistic_regression",
    "random_forest",
    "xgboost",
]

TEST_CASES = [
    {
        "id": "PAY_01",
        "name": "Normal small payment",
        "description": "An ordinary low-value payment with consistent balances.",
        "expected_category": "LOW",
        "transaction": {
            "step": 100,
            "type": "PAYMENT",
            "amount": 500,
            "oldbalanceOrg": 10000,
            "newbalanceOrig": 9500,
            "oldbalanceDest": 5000,
            "newbalanceDest": 5500,
            "isFlaggedFraud": 0,
        },
    },
    {
        "id": "PAY_02",
        "name": "Normal cash withdrawal",
        "description": "A regular cash withdrawal with sufficient sender balance.",
        "expected_category": "LOW",
        "transaction": {
            "step": 120,
            "type": "CASH_OUT",
            "amount": 2000,
            "oldbalanceOrg": 15000,
            "newbalanceOrig": 13000,
            "oldbalanceDest": 0,
            "newbalanceDest": 0,
            "isFlaggedFraud": 0,
        },
    },
    {
        "id": "PAY_03",
        "name": "Normal money transfer",
        "description": "A regular transfer with consistent account balances.",
        "expected_category": "LOW",
        "transaction": {
            "step": 150,
            "type": "TRANSFER",
            "amount": 5000,
            "oldbalanceOrg": 20000,
            "newbalanceOrig": 15000,
            "oldbalanceDest": 10000,
            "newbalanceDest": 15000,
            "isFlaggedFraud": 0,
        },
    },
    {
        "id": "PAY_04",
        "name": "Cash deposit",
        "description": "Provisional CASH_IN scenario; destination balance pattern needs validation.",
        "expected_category": "LOW (provisional)",
        "transaction": {
            "step": 180,
            "type": "CASH_IN",
            "amount": 3000,
            "oldbalanceOrg": 5000,
            "newbalanceOrig": 8000,
            "oldbalanceDest": 10000,
            "newbalanceDest": 7000,
            "isFlaggedFraud": 0,
        },
    },
    {
        "id": "PAY_05",
        "name": "Large transfer with sufficient balance",
        "description": "A high-value transfer with consistent balances.",
        "expected_category": "REVIEW",
        "transaction": {
            "step": 250,
            "type": "TRANSFER",
            "amount": 75000,
            "oldbalanceOrg": 100000,
            "newbalanceOrig": 25000,
            "oldbalanceDest": 50000,
            "newbalanceDest": 125000,
            "isFlaggedFraud": 0,
        },
    },
    {
        "id": "PAY_06",
        "name": "Large cash withdrawal",
        "description": "A withdrawal using most of the sender's available balance.",
        "expected_category": "REVIEW",
        "transaction": {
            "step": 300,
            "type": "CASH_OUT",
            "amount": 90000,
            "oldbalanceOrg": 100000,
            "newbalanceOrig": 10000,
            "oldbalanceDest": 0,
            "newbalanceDest": 0,
            "isFlaggedFraud": 0,
        },
    },
    {
        "id": "PAY_07",
        "name": "Entire sender balance transferred",
        "description": "The transfer completely empties the sender's account.",
        "expected_category": "HIGH",
        "transaction": {
            "step": 350,
            "type": "TRANSFER",
            "amount": 500000,
            "oldbalanceOrg": 500000,
            "newbalanceOrig": 0,
            "oldbalanceDest": 10000,
            "newbalanceDest": 510000,
            "isFlaggedFraud": 0,
        },
    },
    {
        "id": "PAY_08",
        "name": "Transfer exceeds sender balance",
        "description": "An intentionally inconsistent synthetic balance scenario.",
        "expected_category": "HIGH",
        "transaction": {
            "step": 400,
            "type": "TRANSFER",
            "amount": 900000,
            "oldbalanceOrg": 300000,
            "newbalanceOrig": 0,
            "oldbalanceDest": 10000,
            "newbalanceDest": 910000,
            "isFlaggedFraud": 0,
        },
    },
    {
        "id": "PAY_09",
        "name": "Flagged large transfer",
        "description": "A large transfer with the PaySim fraud flag enabled.",
        "expected_category": "HIGH",
        "transaction": {
            "step": 450,
            "type": "TRANSFER",
            "amount": 200000,
            "oldbalanceOrg": 200000,
            "newbalanceOrig": 0,
            "oldbalanceDest": 5000,
            "newbalanceDest": 205000,
            "isFlaggedFraud": 1,
        },
    },
    {
        "id": "PAY_10",
        "name": "Very large account-draining transfer",
        "description": "An extremely large transfer that empties the sender's account.",
        "expected_category": "HIGH",
        "transaction": {
            "step": 500,
            "type": "TRANSFER",
            "amount": 900000,
            "oldbalanceOrg": 900000,
            "newbalanceOrig": 0,
            "oldbalanceDest": 10000,
            "newbalanceDest": 910000,
            "isFlaggedFraud": 0,
        },
    },
]


def serialize_features(features):
    """Safely convert engineered features (DataFrame or dict) into a JSON-safe dict."""
    if hasattr(features, "to_dict"):
        records = features.fillna(0).to_dict(orient="records")
        raw_dict = records[0] if records else {}
    elif isinstance(features, dict):
        raw_dict = features
    else:
        return {}

    return {
        str(k): (v.item() if hasattr(v, "item") else v)
        for k, v in raw_dict.items()
    }


def compare_with_expectation(expected_category, prediction):
    """Compare binary ML output with LOW/HIGH expectations only."""
    if expected_category.startswith("LOW"):
        return "MATCH" if prediction == 0 else "DIFFERENT"

    if expected_category == "HIGH":
        return "MATCH" if prediction == 1 else "DIFFERENT"

    return "MANUAL REVIEW - no direct binary comparison"


@router.post("/run")
def run_paysim_tests():
    """Run all 10 synthetic scenarios through every available ML model."""

    results = []
    available_models = ml_service.available_models()

    for case in TEST_CASES:
        transaction = case["transaction"]
        features = build_features(transaction)

        model_results = {}

        for model_name in MODEL_NAMES:
            if model_name not in available_models:
                model_results[model_name] = {
                    "available": False,
                    "error": f"{model_name} is not loaded.",
                }
                continue

            prediction_result = ml_service.predict(
                transaction,
                model_name=model_name,
            )

            if not prediction_result.get("available"):
                model_results[model_name] = prediction_result
                continue

            probability = float(prediction_result.get("fraud_score") or 0.0)
            prediction = int(prediction_result.get("prediction") or 0)

            model_results[model_name] = {
                "available": True,
                "fraud_probability": probability,
                "fraud_probability_percent": round(probability * 100, 4),
                "prediction": prediction,
                "prediction_label": "FRAUD" if prediction == 1 else "NON-FRAUD",
                "expectation_result": compare_with_expectation(
                    case["expected_category"],
                    prediction,
                ),
            }

        results.append({
            "id": case["id"],
            "scenario": case["name"],
            "description": case["description"],
            "expected_category": case["expected_category"],
            "transaction": transaction,
            "engineered_features": serialize_features(features),
            "model_results": model_results,
        })

    return {
        "message": "PaySim model testing completed.",
        "scenarios_run": len(results),
        "available_models": available_models,
        "results": results,
    }