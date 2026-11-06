"""
AML service for FinShield AI.

Integrates the existing AML analysis modules from code/ml/src with the
FastAPI backend and attaches detailed explanations when available.
"""

import sys
from pathlib import Path

from app.config import AML_HISTORY_LIMIT, REPO_ROOT


# -------------------------------------------------------------------
# 1. Locate and import the existing AML modules
# -------------------------------------------------------------------

ML_DIR = REPO_ROOT / "ml"

if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

try:
    from src.analysis_aml import analyze_aml
    from src.rules_aml import DEFAULT_THRESHOLDS

    AML_AVAILABLE = True
    AML_IMPORT_ERROR = None

except Exception as exc:
    analyze_aml = None
    DEFAULT_THRESHOLDS = {}
    AML_AVAILABLE = False
    AML_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"


# -------------------------------------------------------------------
# 2. Import the detailed AML explanation module
# -------------------------------------------------------------------

generate_detailed_aml_explanation = None
EXPLANATION_IMPORT_ERROR = None

try:
    explanation_file = ML_DIR / "src" / "explanation_aml.py"

    if not explanation_file.is_file():
        raise FileNotFoundError(
            f"Explanation module not found: {explanation_file}"
        )

    from src.explanation_aml import generate_detailed_aml_explanation

except Exception as exc:
    EXPLANATION_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"


# Timestamp format expected by the AML modules
AML_TIME_FORMAT = "%Y/%m/%d %H:%M"


# -------------------------------------------------------------------
# 3. Convert a database transaction into the AML input format
# -------------------------------------------------------------------

def to_aml_dict(transaction) -> dict:
    """Convert a database Transaction row to the AML input format."""
    return {
        "timestamp": transaction.timestamp.strftime(AML_TIME_FORMAT),
        "sender_id": transaction.name_orig,
        "sender_account": transaction.name_orig,
        "receiver_id": transaction.name_dest,
        "receiver_account": transaction.name_dest,
        "amount": float(transaction.amount),
        "currency": transaction.currency,
        "payment_type": transaction.txn_type,
    }


# -------------------------------------------------------------------
# 4. Retrieve previous transactions from the same sender
# -------------------------------------------------------------------

def get_history(db, transaction) -> list[dict]:
    """Get previous transactions from the same sender, newest first."""
    from app.models import Transaction

    rows = (
        db.query(Transaction)
        .filter(
            Transaction.name_orig == transaction.name_orig,
            Transaction.id != transaction.id,
            Transaction.timestamp <= transaction.timestamp,
        )
        .order_by(Transaction.timestamp.desc())
        .limit(AML_HISTORY_LIMIT)
        .all()
    )

    return [to_aml_dict(row) for row in rows]


# -------------------------------------------------------------------
# 5. Analyze the transaction and attach a detailed explanation
# -------------------------------------------------------------------

def analyze(db, transaction) -> dict:
    """
    Run the existing AML analysis and attach a detailed explanation.

    The original AML result is retained if explanation generation fails.
    """
    if not AML_AVAILABLE:
        return {
            "available": False,
            "error": AML_IMPORT_ERROR,
        }

    history = get_history(db, transaction)
    transaction_data = to_aml_dict(transaction)

    try:
        # Run the existing rules, behavior, network, scoring,
        # investigation-summary, and notification modules.
        result = analyze_aml(transaction_data, history)

        if not isinstance(result, dict):
            raise TypeError("analyze_aml() must return a dictionary.")

        result["available"] = True
        result["history_size"] = len(history)

        # Add the detailed explanation without changing the original score.
        if generate_detailed_aml_explanation is not None:
            try:
                detailed = generate_detailed_aml_explanation(
                    transaction_data=transaction_data,
                    transaction_history=history,
                    analysis_result=result,
                )

                if isinstance(detailed, dict):
                    result["detailed_explanation"] = detailed.get(
                        "explanation",
                        "No detailed explanation was generated.",
                    )
                    result["explanation_details"] = detailed
                else:
                    result["explanation_error"] = (
                        "The explanation function did not return a dictionary."
                    )

            except Exception as exc:
                result["explanation_error"] = (
                    f"{type(exc).__name__}: {exc}"
                )
        else:
            result["explanation_error"] = EXPLANATION_IMPORT_ERROR

        return result

    except Exception as exc:
        return {
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


# -------------------------------------------------------------------
# 6. Return AML rule thresholds
# -------------------------------------------------------------------

def get_thresholds() -> dict:
    """Return the default thresholds used by the AML rule engine."""
    return dict(DEFAULT_THRESHOLDS)
