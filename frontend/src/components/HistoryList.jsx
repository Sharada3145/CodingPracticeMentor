import { useState } from "react";

function MistakeBadge({ type, confidence }) {
  return (
    <>
      <span className={`badge ${type}`}>{type}</span>
      <span className="confidence-badge">{confidence || "medium"}</span>
    </>
  );
}

function shortNote(text) {
  if (!text) return "No feedback note available.";
  const firstSentence = text.split(".")[0]?.trim();
  return firstSentence ? `${firstSentence}.` : text;
}

export default function HistoryList({ attempts }) {
  const [showAll, setShowAll] = useState(false);
  const [expanded, setExpanded] = useState({});

  const visibleAttempts = showAll ? attempts : attempts.slice(0, 5);

  function toggleDetails(id) {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  return (
    <section className="card">
      <h2>Attempt History</h2>
      {attempts.length === 0 ? (
        <p>No attempts yet.</p>
      ) : (
        <>
          <ul className="history-list">
          {visibleAttempts.map((attempt) => (
            <li key={attempt.id} className="history-item">
              <div className="history-top">
                <strong>{attempt.problem_name}</strong>
                <MistakeBadge type={attempt.mistake_type} confidence={attempt.confidence} />
              </div>
              <p className="muted">
                {attempt.preferred_language} • {new Date(attempt.created_at).toLocaleString()}
              </p>
              <p>{shortNote(attempt.generated_feedback)}</p>
              <button className="details-btn" onClick={() => toggleDetails(attempt.id)}>
                {expanded[attempt.id] ? "Hide details" : "Show details"}
              </button>
              {expanded[attempt.id] && (
                <div className="history-details">
                  <p className="note">Pattern: {attempt.repeated_pattern_notes}</p>
                  <p className="note">Recommendation: {attempt.recommendation_notes}</p>
                  <p className="note">Full feedback: {attempt.generated_feedback}</p>
                </div>
              )}
            </li>
          ))}
        </ul>
          {attempts.length > 5 && (
            <button className="details-btn" onClick={() => setShowAll((prev) => !prev)}>
              {showAll ? "Show recent 5" : `Show all ${attempts.length}`}
            </button>
          )}
        </>
      )}
    </section>
  );
}