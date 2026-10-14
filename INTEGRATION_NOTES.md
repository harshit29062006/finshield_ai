# Backend Integration Notes

Import:
```python
from aml.aml_analysis import analyze_aml
```

Call:
```python
result = analyze_aml(transaction_data, transaction_history)
```

Common input fields:
`timestamp`, `sender_id`, `sender_account`, `receiver_id`, `receiver_account`,
`amount`, `currency`, `payment_type`.

Suggested PostgreSQL fields:
- aml_score
- behavior_score
- network_score
- risk_level
- triggered_rules
- reasons

The backend can combine `aml_score` with the team's ML fraud score for hybrid scoring.

A HIGH score is a screening signal for investigator review, not proof of a crime.
