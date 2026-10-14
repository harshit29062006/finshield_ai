"""Basic relationship/network analysis without external graph packages."""
from collections import Counter
def analyze_network(transaction, history=None):
    history = history or []
    sender, receiver = transaction.get("sender_id",""), transaction.get("receiver_id","")
    edges = [(h.get("sender_id"),h.get("receiver_id")) for h in history]
    edges.append((sender,receiver))
    outgoing = Counter(a for a,b in edges if a)
    incoming = Counter(b for a,b in edges if b)
    score, reasons = 0.0, []
    if outgoing[sender] >= 5:
        score += 0.30; reasons.append("Sender is connected to many transactions.")
    if incoming[receiver] >= 5:
        score += 0.30; reasons.append("Receiver is connected to many incoming transactions.")
    if (receiver,sender) in edges:
        score += 0.40; reasons.append("A reciprocal transfer relationship was observed.")
    if not reasons:
        reasons.append("No strong relationship anomaly was found in the supplied history.")
    return {"network_score":min(score,1.0), "reasons":reasons}
