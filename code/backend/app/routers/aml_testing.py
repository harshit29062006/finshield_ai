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
        "name": "01 - Normal low-value transaction",
        "description": "Baseline test with no suspicious indicators.",
        "amount": 500,
        "sender": "S01",
        "receiver": "R01",
        "history": [],
    },
    {
        "name": "02 - Amount just below high-value threshold",
        "description": "Checks whether HIGH_AMOUNT stays inactive below 100,000.",
        "amount": 99999,
        "sender": "S02",
        "receiver": "R02",
        "history": [],
    },
    {
        "name": "03 - Amount at high-value threshold",
        "description": "Checks the HIGH_AMOUNT threshold at 100,000.",
        "amount": 100000,
        "sender": "S03",
        "receiver": "R03",
        "history": [],
    },
    {
        "name": "04 - New receiver below large-transfer threshold",
        "description": "Checks the new-receiver amount threshold below 50,000.",
        "amount": 49999,
        "sender": "S04",
        "receiver": "R04_NEW",
        "history": [
            {"amount": 1000, "receiver": "R04_OLD1", "minutes_ago": 120},
            {"amount": 1200, "receiver": "R04_OLD2", "minutes_ago": 60},
        ],
    },
    {
        "name": "05 - Large transfer to a new receiver",
        "description": "Checks NEW_RECEIVER_LARGE_AMOUNT and unusual amount behaviour.",
        "amount": 60000,
        "sender": "S05",
        "receiver": "R05_NEW",
        "history": [
            {"amount": 1000, "receiver": "R05_OLD1", "minutes_ago": 120},
            {"amount": 2000, "receiver": "R05_OLD2", "minutes_ago": 60},
        ],
    },
    {
        "name": "06 - Four transactions in 24 hours",
        "description": "Checks frequency when four transactions exist including current.",
        "amount": 1000,
        "sender": "S06",
        "receiver": "R06",
        "history": [
            {"amount": 900, "receiver": "R06", "minutes_ago": 50},
            {"amount": 850, "receiver": "R06", "minutes_ago": 40},
            {"amount": 800, "receiver": "R06", "minutes_ago": 30},
        ],
    },
    {
        "name": "07 - Five transactions in 24 hours",
        "description": "Checks HIGH_FREQUENCY at five transactions including current.",
        "amount": 1000,
        "sender": "S07",
        "receiver": "R07",
        "history": [
            {"amount": 900, "receiver": "R07", "minutes_ago": 50},
            {"amount": 850, "receiver": "R07", "minutes_ago": 40},
            {"amount": 800, "receiver": "R07", "minutes_ago": 30},
            {"amount": 750, "receiver": "R07", "minutes_ago": 20},
        ],
    },
    {
        "name": "08 - Behaviour ratio around 2x",
        "description": "Checks behaviour scoring around the 2x historical-average boundary.",
        "amount": 2000,
        "sender": "S08",
        "receiver": "R08_NEW",
        "history": [
            {"amount": 1000, "receiver": "R08_A", "minutes_ago": 120},
            {"amount": 1000, "receiver": "R08_B", "minutes_ago": 60},
        ],
    },
    {
        "name": "09 - Behaviour ratio around 3x",
        "description": "Checks behaviour scoring around the 3x historical-average boundary.",
        "amount": 3000,
        "sender": "S09",
        "receiver": "R09_NEW",
        "history": [
            {"amount": 1000, "receiver": "R09_A", "minutes_ago": 120},
            {"amount": 1000, "receiver": "R09_B", "minutes_ago": 60},
        ],
    },
    {
        "name": "10 - Behaviour ratio around 5x",
        "description": "Checks behaviour scoring around the 5x historical-average boundary.",
        "amount": 5000,
        "sender": "S10",
        "receiver": "R10_NEW",
        "history": [
            {"amount": 1000, "receiver": "R10_A", "minutes_ago": 120},
            {"amount": 1000, "receiver": "R10_B", "minutes_ago": 60},
        ],
    },
    {
        "name": "11 - Sender connected to multiple receivers",
        "description": "Checks network risk from a sender connected to many receivers.",
        "amount": 2000,
        "sender": "S11",
        "receiver": "R11_NEW",
        "history": [
            {"amount": 1000, "receiver": "R11_A", "minutes_ago": 110},
            {"amount": 1100, "receiver": "R11_B", "minutes_ago": 100},
            {"amount": 1200, "receiver": "R11_C", "minutes_ago": 90},
            {"amount": 1300, "receiver": "R11_D", "minutes_ago": 80},
            {"amount": 1400, "receiver": "R11_E", "minutes_ago": 70},
        ],
    },
    {
        "name": "12 - Receiver connected to multiple senders",
        "description": "Checks network risk from many incoming transfers to one receiver.",
        "amount": 2000,
        "sender": "S12",
        "receiver": "R12",
        "history": [
            {"sender": "S12_A", "amount": 1000, "receiver": "R12", "minutes_ago": 110},
            {"sender": "S12_B", "amount": 1100, "receiver": "R12", "minutes_ago": 100},
            {"sender": "S12_C", "amount": 1200, "receiver": "R12", "minutes_ago": 90},
            {"sender": "S12_D", "amount": 1300, "receiver": "R12", "minutes_ago": 80},
            {"sender": "S12_E", "amount": 1400, "receiver": "R12", "minutes_ago": 70},
        ],
    },
    {
        "name": "13 - Reciprocal transaction relationship",
        "description": "Checks reciprocal sender-receiver relationship detection.",
        "amount": 5000,
        "sender": "S13",
        "receiver": "R13",
        "history": [
            {"sender": "R13", "amount": 4500, "receiver": "S13", "minutes_ago": 30},
        ],
    },
    {
        "name": "14 - Combined high-risk indicators",
        "description": "Combines high amount, new receiver, frequency and unusual behaviour.",
        "amount": 150000,
        "sender": "S14",
        "receiver": "R14_NEW",
        "history": [
            {"amount": 1000, "receiver": "R14_A", "minutes_ago": 110},
            {"amount": 1000, "receiver": "R14_B", "minutes_ago": 100},
            {"amount": 1000, "receiver": "R14_C", "minutes_ago": 90},
            {"amount": 1000, "receiver": "R14_D", "minutes_ago": 80},
            {"amount": 1000, "receiver": "R14_E", "minutes_ago": 70},
        ],
    },
    {
        "name": "15 - Stable customer activity",
        "description": "Checks whether consistent historical activity receives a low score.",
        "amount": 1000,
        "sender": "S15",
        "receiver": "R15",
        "history": [
            {"amount": 950, "receiver": "R15", "minutes_ago": 1440},
            {"amount": 1050, "receiver": "R15", "minutes_ago": 1320},
            {"amount": 1000, "receiver": "R15", "minutes_ago": 1200},
            {"amount": 980, "receiver": "R15", "minutes_ago": 1080},
            {"amount": 1020, "receiver": "R15", "minutes_ago": 960},
            {"amount": 990, "receiver": "R15", "minutes_ago": 840},
            {"amount": 1010, "receiver": "R15", "minutes_ago": 720},
            {"amount": 1000, "receiver": "R15", "minutes_ago": 600},
            {"amount": 970, "receiver": "R15", "minutes_ago": 480},
            {"amount": 1030, "receiver": "R15", "minutes_ago": 360},
        ],
    },
    {
        "name": "16 - Standalone high-value transaction",
        "description": "Tests a 150,000 high-value transaction without other suspicious indicators.",
        "amount": 150000,
        "sender": "S16",
        "receiver": "R16",
        "history": [],
    },
    {
        "name": "17 - Six repeated transactions in 24 hours",
        "description": "Checks HIGH_FREQUENCY with six transactions including current.",
        "amount": 1000,
        "sender": "S17",
        "receiver": "R17",
        "history": [
            {"amount": 900, "receiver": "R17", "minutes_ago": 50},
            {"amount": 850, "receiver": "R17", "minutes_ago": 40},
            {"amount": 800, "receiver": "R17", "minutes_ago": 30},
            {"amount": 750, "receiver": "R17", "minutes_ago": 20},
            {"amount": 700, "receiver": "R17", "minutes_ago": 10},
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
    """Run all 17 AML test scenarios and roll back their database records."""

    results = []
    savepoint = None

    try:
        savepoint = db.begin_nested()
        base_time = datetime.utcnow()

        for scenario_index, scenario in enumerate(SCENARIOS):
            test_time = base_time + timedelta(minutes=scenario_index)

            for history_index, item in enumerate(scenario["history"]):
                minutes_ago = item.get(
                    "minutes_ago", len(scenario["history"]) - history_index
                )
                history_time = test_time - timedelta(minutes=minutes_ago)
                history_sender = item.get("sender", scenario["sender"])

                historical = create_transaction(
                    sender=history_sender,
                    receiver=item["receiver"],
                    amount=item["amount"],
                    timestamp=history_time,
                    step=history_index + 1,
                )
                db.add(historical)

            db.flush()

            target = create_transaction(
                sender=scenario["sender"],
                receiver=scenario["receiver"],
                amount=scenario["amount"],
                timestamp=test_time,
                step=len(scenario["history"]) + 1,
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