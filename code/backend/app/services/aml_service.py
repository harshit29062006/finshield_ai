"""
Wrapper around Member 4's AML package.

Member 4's code is imported as-is from the `member4_aml` folder. The only work
done here is translating between my database columns and the field names their
`analyze_aml()` function expects, and formatting timestamps as "%Y/%m/%d %H:%M"
because that is the only format their rule engine parses.
"""
import sys

from app.config import AML_HISTORY_LIMIT, AML_PACKAGE_DIR

# Make Member 4's package importable without copying their code into my folder.
if str(AML_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(AML_PACKAGE_DIR))

try:
    from aml.aml_analysis import analyze_aml           # Member 4's entry point
    from aml.rules import DEFAULT_THRESHOLDS           # shown on the admin screen

    AML_AVAILABLE = True
    AML_IMPORT_ERROR = None
except Exception as exc:                               # noqa: BLE001
    analyze_aml = None
    DEFAULT_THRESHOLDS = {}
    AML_AVAILABLE = False
    AML_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"

# Member 4's rules.py parses timestamps with this format only.
AML_TIME_FORMAT = "%Y/%m/%d %H:%M"


def to_aml_dict(transaction) -> dict:
    """Convert a Transaction row into the dict shape Member 4 documented."""
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


def get_history(db, transaction) -> list[dict]:
    """
    Past transactions of the same sender, newest first.

    Member 4's rules, behaviour and network analysis all need this history;
    without it every transaction looks like a first-time customer.
    """
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


def analyze(db, transaction) -> dict:
    """Run Member 4's AML analysis on one stored transaction."""
    if not AML_AVAILABLE:
        return {"available": False, "error": AML_IMPORT_ERROR}

    history = get_history(db, transaction)
    try:
        result = analyze_aml(to_aml_dict(transaction), history)
        result["available"] = True
        result["history_size"] = len(history)
        return result
    except Exception as exc:                           # noqa: BLE001
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def get_thresholds() -> dict:
    """Current rule thresholds, so an admin can see what the engine uses."""
    return dict(DEFAULT_THRESHOLDS)
