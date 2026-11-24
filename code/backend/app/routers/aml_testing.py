"""Admin-only AML scenario testing endpoint for 17 scenarios."""

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


# Helper for defining historical transactions.
def history(receiver, amount, minutes_before=60, sender=None, hours_before=0):
    return {
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "minutes_before": minutes_before,
        "hours_before": hours_before,
    }


# All 17 AML test scenarios.
SCENARIOS = [
    {
        "name": "01 - Normal low-value transaction",
        "description": "Baseline test with no suspicious indicators.",
        "amount": 500,
        "sender": "S01",
        "receiver": "R01",
        "history": [],
    },
    {
        "name": "02 - Amount just below high-value threshold",
        "description": "Checks a transaction of 99,999, just below 100,000.",
        "amount": 99999,
        "sender": "S02",
        "receiver": "R02",
        "history": [],
    },
    {
        "name": "03 - Amount at high-value threshold",
        "description": "Checks the high-value threshold at 100,000.",
        "amount": 100000,
        "sender": "S03",
        "receiver": "R03",
        "history": [],
    },
    {
        "name": "04 - New receiver below large-transfer threshold",
        "description": "Tests a 49,999 payment to a new receiver.",
        "amount": 49999,
        "sender": "S04",
        "receiver": "R04_NEW",
        "history": [
            history("R04_OLD1", 1000, minutes_before=120),
            history("R04_OLD2", 1200, minutes_before=60),
        ],
    },
    {
        "name": "05 - Large transfer to a new receiver",
        "description": "Tests a 60,000 payment to a new receiver.",
        "amount": 60000,
        "sender": "S05",
        "receiver": "R05_NEW",
        "history": [
            history("R05_OLD1", 1000, minutes_before=120),
            history("R05_OLD2", 2000, minutes_before=60),
        ],
    },
    {
        "name": "06 - Four transactions in 24 hours",
        "description": "Three historical transactions plus the current transaction.",
        "amount": 1000,
        "sender": "S06",
        "receiver": "R06",
        "history": [
            history("R06", 900, minutes_before=50),
            history("R06", 850, minutes_before=40),
            history("R06", 800, minutes_before=30),
        ],
    },
    {
        "name": "07 - Five transactions in 24 hours",
        "description": "Four historical transactions plus the current transaction.",
        "amount": 1000,
        "sender": "S07",
        "receiver": "R07",
        "history": [
            history("R07", 900, minutes_before=50),
            history("R07", 850, minutes_before=40),
            history("R07", 800, minutes_before=30),
            history("R07", 750, minutes_before=20),
        ],
    },
    {
        "name": "08 - Behaviour ratio around 2x",
        "description": "Tests a transaction around twice the historical average.",
        "amount": 2000,
        "sender": "S08",
        "receiver": "R08_NEW",
        "history": [
            history("R08_A", 1000, minutes_before=120),
            history("R08_B", 1000, minutes_before=60),
        ],
    },
    {
        "name": "09 - Behaviour ratio around 3x",
        "description": "Tests a transaction around three times the historical average.",
        "amount": 3000,
        "sender": "S09",
        "receiver": "R09_NEW",
        "history": [
            history("R09_A", 1000, minutes_before=120),
            history("R09_B", 1000, minutes_before=60),
        ],
    },
    {
        "name": "10 - Behaviour ratio around 5x",
        "description": "Tests a transaction around five times the historical average.",
        "amount": 5000,
        "sender": "S10",
        "receiver": "R10_NEW",
        "history": [
            history("R10_A", 1000, minutes_before=120),
            history("R10_B", 1000, minutes_before=60),
        ],
    },
    {
        "name": "11 - Sender connected to multiple receivers",
        "description": "Tests network risk from one sender paying many receivers.",
        "amount": 2000,
        "sender": "S11",
        "receiver": "R11_NEW",
        "history": [
            history("R11_A", 1000, minutes_before=110),
            history("R11_B", 1100, minutes_before=100),
            history("R11_C", 1200, minutes_before=90),
            history("R11_D", 1300, minutes_before=80),
            history("R11_E", 1400, minutes_before=70),
        ],
    },
    {
        "name": "12 - Receiver connected to multiple senders",
        "description": "Tests network risk from many senders paying one receiver.",
        "amount": 2000,
        "sender": "S12",
        "receiver": "R12",
        "history": [
            history("R12", 1000, minutes_before=110, sender="S12_A"),
            history("R12", 1100, minutes_before=100, sender="S12_B"),
            history("R12", 1200, minutes_before=90, sender="S12_C"),
            history("R12", 1300, minutes_before=80, sender="S12_D"),
            history("R12", 1400, minutes_before=70, sender="S12_E"),
        ],
    },
    {
        "name": "13 - Reciprocal transaction relationship",
        "description": "Tests transactions between two accounts in both directions.",
        "amount": 5000,
        "sender": "S13",
        "receiver": "R13",
        "history": [
            history("S13", 4500, minutes_before=30, sender="R13"),
        ],
    },
    {
        "name": "14 - Combined high-risk indicators",
        "description": "Combines high amount, new receiver and multiple previous receivers.",
        "amount": 150000,
        "sender": "S14",
        "receiver": "R14_NEW",
        "history": [
            history("R14_A", 1000, minutes_before=110),
            history("R14_B", 1000, minutes_before=100),
            history("R14_C", 1000, minutes_before=90),
            history("R14_D", 1000, minutes_before=80),
            history("R14_E", 1000, minutes_before=70),
        ],
    },
    {
        "name": "15 - Stable customer activity",
        "description": "Tests consistent historical activity with similar transaction amounts.",
        "amount": 1000,
        "sender": "S15",
        "receiver": "R15",
        "history": [
            history("R15", 950, hours_before=26),
            history("R15", 1050, hours_before=24),
            history("R15", 1000, hours_before=22),
            history("R15", 980, hours_before=20),
            history("R15", 1020, hours_before=18),
            history("R15", 990, hours_before=16),
            history("R15", 1010, hours_before=14),
            history("R15", 1000, hours_before=10),
            history("R15", 970, hours_before=8),
            history("R15", 1030, hours_before=6),
        ],
    },
    {
        "name": "16 - Standalone high-value transaction",
        "description": "Tests a 150,000 transaction without other suspicious indicators.",
        "amount": 150000,
        "sender": "S16",
        "receiver": "R16",
        "history": [],
    },
    {
        "name": "17 - Six repeated transactions in 24 hours",
        "description": "Five historical transactions plus the current transaction.",
        "amount": 1000,
        "sender": "S17",
        "receiver": "R17",
        "history": [
            history("R17", 900, minutes_before=50),
            history("R17", 850, minutes_before=40),
            history("R17", 800, minutes_before=30),
            history("R17", 750, minutes_before=20),
            history("R17", 700, minutes_before=10),
        ],
    },
]


def create_transaction(sender, receiver, amount, timestamp, step):
    sender_balance = max(amount * 10, 1000000)

    return Transaction(
        txn_ref=f"AMLTEST-{uuid.uuid4().hex[:12].upper()}",
        step=step,
        txn_type="TRANSFER",
        amount=float(amount),
        name_orig=sender,
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
    """Run all 17 AML scenarios and roll back their database records."""

    results = []
    savepoint = None

    try:
        savepoint = db.begin_nested()
        base_time = datetime.utcnow() - timedelta(minutes=30)

        for scenario_index, scenario in enumerate(SCENARIOS):
            test_time = base_time + timedelta(minutes=scenario_index * 10)

            # Insert historical transactions for this scenario.
            for history_index, item in enumerate(scenario["history"]):
                history_time = test_time - timedelta(
                    days=item.get("days_before", 0),
                    hours=item.get("hours_before", 0),
                    minutes=item.get("minutes_before", 60),
                )

                historical = create_transaction(
                    item.get("sender") or scenario["sender"],
                    item["receiver"],
                    item["amount"],
                    history_time,
                    history_index + 1,
                )
                db.add(historical)

            db.flush()

            # Insert the transaction being tested.
            target = create_transaction(
                scenario["sender"],
                scenario["receiver"],
                scenario["amount"],
                test_time,
                100 + scenario_index,
            )
            db.add(target)
            db.flush()

            # Run the same analysis pipeline used by the application.
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

        # Remove all test transactions, risk results and alerts.
        savepoint.rollback()
        db.expire_all()

        return {
            "message": "All 17 AML scenarios completed. Test records were rolled back.",
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