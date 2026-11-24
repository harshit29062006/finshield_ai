
import { useState } from "react";
import { api } from "../api";

export default function PaySimTesting() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [models, setModels] = useState([]);

  const runTests = async () => {
    setLoading(true);
    setError("");
    setMessage("");
    setResults([]);

    try {
      const response = await api.runPaySimTests();
      setResults(response.results || []);
      setModels(response.available_models || []);
      setMessage(response.message || "PaySim tests completed.");
    } catch (err) {
      setError(err.message || "Unable to run PaySim tests.");
    } finally {
      setLoading(false);
    }
  };

  const riskColor = (level) => {
    if (level === "HIGH") return "#dc2626";
    if (level === "LOW") return "#16a34a";
    return "#d97706";
  };

  const modelNames = [
    ["logistic_regression", "Logistic Regression"],
    ["random_forest", "Random Forest"],
    ["xgboost", "XGBoost"],
  ];

  return (
    <div style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>PaySim Model Testing</h1>

      <p>
        Run 10 controlled PaySim scenarios through Logistic Regression,
        Random Forest and XGBoost to evaluate fraud detection.
      </p>

      <button
        onClick={runTests}
        disabled={loading}
        style={{
          padding: "12px 20px",
          border: "none",
          borderRadius: "8px",
          background: loading ? "#94a3b8" : "#2563eb",
          color: "white",
          cursor: loading ? "not-allowed" : "pointer",
          fontWeight: "bold",
        }}
      >
        {loading ? "Running tests..." : "Run All PaySim Tests"}
      </button>

      {message && <p style={{ color: "#16a34a" }}>{message}</p>}
      {error && <p style={{ color: "#dc2626" }}>{error}</p>}

      {results.length > 0 && (
        <>
          <h2>Results ({results.length}/10)</h2>

          <p>
            Models available: {models.join(", ")}
          </p>

          {results.map((item) => (
            <div
              key={item.id}
              style={{
                border: "1px solid #d1d5db",
                borderRadius: "12px",
                padding: "20px",
                marginBottom: "20px",
                background: "var(--card-bg, white)",
              }}
            >
              <h2>{item.id} – {item.scenario}</h2>
              <p>{item.description}</p>

              <p>
                <strong>Expected category:</strong>{" "}
                <span style={{ color: riskColor(item.expected_category) }}>
                  {item.expected_category}
                </span>
              </p>

              <h3>Transaction details</h3>

              <p>Type: {item.transaction.type}</p>
              <p>Amount: ${Number(item.transaction.amount).toLocaleString()}</p>
              <p>Step: {item.transaction.step}</p>
              <p>Sender old balance: ${Number(item.transaction.oldbalanceOrg).toLocaleString()}</p>
              <p>Sender new balance: ${Number(item.transaction.newbalanceOrig).toLocaleString()}</p>
              <p>Receiver old balance: ${Number(item.transaction.oldbalanceDest).toLocaleString()}</p>
              <p>Receiver new balance: ${Number(item.transaction.newbalanceDest).toLocaleString()}</p>
              <p>Flagged fraud: {item.transaction.isFlaggedFraud}</p>

              <h3>Model predictions</h3>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: "14px",
                }}
              >
                {modelNames.map(([key, label]) => {
                  const result = item.model_results?.[key];

                  return (
                    <div
                      key={key}
                      style={{
                        border: "1px solid #d1d5db",
                        borderRadius: "8px",
                        padding: "14px",
                      }}
                    >
                      <h4>{label}</h4>

                      {!result?.available ? (
                        <p style={{ color: "#dc2626" }}>
                          {result?.error || "Model unavailable"}
                        </p>
                      ) : (
                        <>
                          <p>
                            <strong>Fraud probability:</strong>{" "}
                            {(result.fraud_probability_percent).toFixed(4)}%
                          </p>
                          <p>
                            <strong>Prediction:</strong>{" "}
                            {result.prediction_label}
                          </p>
                          <p>
                            <strong>Binary output:</strong>{" "}
                            {result.prediction}
                          </p>
                          <p>
                            <strong>Expectation:</strong>{" "}
                            {result.expectation_result}
                          </p>
                        </>
                      )}
                    </div>
                  );
                })}
              </div>

              <details style={{ marginTop: "16px" }}>
                <summary>View 18 engineered features</summary>
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr>
                        <th style={{ textAlign: "left", padding: "8px" }}>Feature</th>
                        <th style={{ textAlign: "left", padding: "8px" }}>Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(item.engineered_features || {}).map(
                        ([feature, value]) => (
                          <tr key={feature}>
                            <td style={{ padding: "8px", borderTop: "1px solid #ddd" }}>
                              {feature}
                            </td>
                            <td style={{ padding: "8px", borderTop: "1px solid #ddd" }}>
                              {typeof value === "number" ? value.toFixed(4) : String(value)}
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>
              </details>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
