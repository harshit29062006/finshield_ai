# Verification

Unit tests return code: 0
Dataset parser return code: 0
Example AML analysis return code: 0

## Dataset parser output
Parsed transactions: 13670
Laundering patterns: 75
- LAUNDERING ATTEMPT - SCATTER-GATHER: 2453
- LAUNDERING ATTEMPT - STACK: 2117
- LAUNDERING ATTEMPT - BIPARTITE: 1220
- LAUNDERING ATTEMPT - GATHER-SCATTER:  Max 11-degree Fan-In: 258
- LAUNDERING ATTEMPT - GATHER-SCATTER:  Max 13-degree Fan-In: 256
- LAUNDERING ATTEMPT - GATHER-SCATTER:  Max 15-degree Fan-In: 251
- LAUNDERING ATTEMPT - GATHER-SCATTER:  Max 10-degree Fan-In: 218
- LAUNDERING ATTEMPT - GATHER-SCATTER:  Max 4-degree Fan-In: 207
- LAUNDERING ATTEMPT - GATHER-SCATTER:  Max 12-degree Fan-In: 203
- LAUNDERING ATTEMPT - FAN-OUT:  Max 16-degree Fan-Out: 192
First parsed row: {'timestamp': '2022/08/09 05:14', 'sender_id': '00952', 'sender_account': '8139F54E0', 'receiver_id': '0111632', 'receiver_account': '8062C56E0', 'amount': 5331.44, 'currency': 'US Dollar', 'converted_amount': 5331.44, 'converted_currency': 'US Dollar', 'payment_type': 'ACH', 'label': 1, 'laundering_pattern': 'LAUNDERING ATTEMPT - STACK'}


## Example AML analysis output
aml_score: 0.6675
risk_level: MEDIUM
triggered_rules: ['HIGH_AMOUNT', 'NEW_RECEIVER_LARGE_AMOUNT', 'SUDDEN_ACTIVITY_SPIKE']
rule_score: 0.65
behavior_score: 0.9
network_score: 0.3
reasons: ['Transaction amount is unusually high.', 'Large transfer to a receiver not previously seen in the history.', "Current transaction is much larger than the sender's historical average.", 'Transaction is at least five times the historical average.', 'Sender is connected to many transactions.']
investigation_summary: Transaction C100 -> C999 has AML score 0.67 and risk level MEDIUM.
notification: {'should_notify': True, 'channels': ['dashboard', 'email'], 'message': "FinShield AML Alert: MEDIUM risk transaction. AML score=0.67. Transaction amount is unusually high. Large transfer to a receiver not previously seen in the history. Current transaction is much larger than the sender's historical average."}

