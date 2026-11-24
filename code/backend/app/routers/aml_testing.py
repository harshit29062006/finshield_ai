
"""Admin-only AML scenario testing endpoint."""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import ROLE_ADMIN, Transaction
from app.routers.transactions import run_analysis

router = APIRouter(
    prefix="/api/admin/aml-testing",
    tags=["AML Testing"],
    dependencies=[Depends(require_roles(ROLE_ADMIN))],
)

SCENARIOS = [
    {
        "name": "Normal transaction",
        "description": "A routine transaction with no suspicious history.",
        "amount": 500,
        "sender": "TEST_NORMAL_SENDER",
        "receiver": "TEST_NORMAL_RECEIVER",
        "history": [],
    },
    {
        "name": "High-value transaction",
        "description": "A large transfer with no previous transaction history.",
        "amount": 150000,
        "sender": "TEST_HIGH_SENDER",
        "receiver": "TEST_HIGH_RECEIVER",
        "history": [],
    },
    {
        "name": "New receiver",
        "description": "A large payment to a new receiver after previous activity.",
        "amount": 60000,
        "sender": "TEST_NEW_SENDER",
        "receiver": "TEST_NEW_RECEIVER",
        "history": [
            {"amount": 1000, "receiver": "TEST_OLD_R1"},
            {"amount": 1200, "receiver": "TEST_OLD_R2"},
        ],
    },
    {
        "name": "Repeated transactions",
        "description": "Repeated payments to the same receiver.",
        "amount": 1000,
        "sender": "TEST_REPEAT_SENDER",
        "receiver": "TEST_REPEAT_RECEIVER",
        "history": [
            {"amount": 1000, "receiver": "TEST_REPEAT_RECEIVER"}
            for _ in range(5)
        ],
    },
    {
        "name": "Multiple receivers",
        "description": "One sender making payments to several receivers.",
        "amount": 2000,
        "sender": "TEST_NETWORK_SENDER",
        "receiver": "TEST_NETWORK_NEW_RECEIVER",
        "history": [
            {"amount": 2000, "receiver": f"TEST_NETWORK_R{i}"}
            for i in range(5)
        ],
    },
]


def create_transaction(scenario, receiver, amount, timestamp, step):
    sender_balance = max(amount * 10, 1000000)

    return Transaction(
        txn_ref=f"AMLTEST-{uuid.uuid4().hex[:12].upper()}",
        step=step,
        txn_type="TRANSFER",
        amount=float(amount),
        name_orig=scenario["sender"],
        oldbalance_org=float(sender_balance),
        newbalance_orig=float(sender_balance - amount),
        name_dest=receiver,
        oldbalance_dest=0.0,
        newbalance_dest=float(amount),
        is_flagged_fraud=0,
        currency="US Dollar",
        timestamp=timestamp,
        submitted_by_id=None,
    )


@router.post("/run")
def run_aml_scenarios(db: Session = Depends(get_db)):
    """Run five test scenarios and roll back their database records."""

    results = []
    savepoint = None

    try:
        savepoint = db.begin_nested()
        base_time = datetime.utcnow() - timedelta(minutes=30)

        for scenario_index, scenario in enumerate(SCENARIOS):
            test_time = base_time + timedelta(
                minutes=scenario_index * 10
            )

            for history_index, item in enumerate(scenario["history"]):
                history_time = test_time - timedelta(
                    minutes=len(scenario["history"]) - history_index
                )

                historical = create_transaction(
                    scenario,
                    item["receiver"],
                    item["amount"],
                    history_time,
                    history_index + 1,
                )
                db.add(historical)

            db.flush()

            target = create_transaction(
                scenario,
                scenario["receiver"],
                scenario["amount"],
                test_time,
                10 + scenario_index,
            )
            db.add(target)
            db.flush()

            risk, extras = run_analysis(db, target, commit=False)

            results.append({
                "scenario": scenario["name"],
                "description": scenario["description"],
                "transaction": {
                    "amount": target.amount,
                    "sender": target.name_orig,
                    "receiver": target.name_dest,
                },
                "ml_score": risk.ml_fraud_score,
                "ml_prediction": risk.ml_prediction,
                "aml_score": risk.aml_score,
                "aml_risk_level": risk.aml_risk_level,
                "hybrid_score": risk.final_risk_score,
                "hybrid_risk_level": risk.risk_level,
                "triggered_rules": risk.triggered_rules or [],
                "reasons": risk.reasons or [],
                "investigation_summary": risk.investigation_summary,
                "aml_explanation": extras.get("aml_explanation"),
            })

        # Undo all test inserts, risk results and alerts.
        savepoint.rollback()
        db.expire_all()

        return {
            "message": "AML scenarios completed. Test records were rolled back.",
            "scenarios_run": len(results),
            "test_data_saved": False,
            "results": results,
        }

    except Exception as exc:
        if savepoint is not None and savepoint.is_active:
            savepoint.rollback()
        db.expire_all()
        raise HTTPException(
            status_code=500,
            detail=f"AML scenario testing failed: {str(exc)}",
        ) from exc
