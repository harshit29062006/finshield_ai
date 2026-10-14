# FinShield AI — Member 4: AML + Intelligence

Final prototype folder for Member 4.

## Dataset
`data/amlsim_laundering_attempts.txt` contains the AMLSim laundering-attempt data supplied for this project.
The supplied data has labelled patterns such as STACK, CYCLE, FAN-IN, FAN-OUT, SCATTER-GATHER,
GATHER-SCATTER, BIPARTITE and RANDOM.

## Pipeline
AMLSim data -> preprocessing -> AML rules -> behaviour analysis -> network analysis
-> AML risk score -> risk level -> reasons/alert -> investigation assistant.

## Main interface
```python
from aml.aml_analysis import analyze_aml
result = analyze_aml(transaction_data, transaction_history=None)
```

Returns `aml_score` (0-1), `risk_level`, `triggered_rules`, `rule_score`,
`behavior_score`, `network_score`, `reasons`, `investigation_summary`, and `notification`.

## Prototype scoring
AML score = 45% rule score + 35% behaviour score + 20% network score.
HIGH >= 0.70, MEDIUM >= 0.40, otherwise LOW.

These weights/thresholds are prototype assumptions and should be documented by the team.

## Run
```bash
python examples/example_aml_analysis.py
python examples/dataset_analysis.py
python -m unittest discover tests
```

## Limitations
The uploaded source is a text export of laundering-attempt blocks, not a clean CSV, so a tolerant
parser is included. If the original Kaggle CSV files are later supplied, the mapper can be extended.
The investigation assistant is a deterministic placeholder (no API key required), and notification
code only builds payloads; it does not send real messages.
