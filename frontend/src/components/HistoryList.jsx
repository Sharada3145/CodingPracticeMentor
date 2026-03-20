function MistakeBadge({ type }) {
  return <span className={`badge ${type}`}>{type}</span>;
}

export default function HistoryList({ attempts }) {
  return (
    <section className="card">
      <h2>Attempt History</h2>
      {attempts.length === 0 ? (
        <p>No attempts yet.</p>
      ) : (
        <ul className="history-list">
          {attempts.map((attempt) => (
            <li key={attempt.id} className="history-item">
              <div className="history-top">
                <strong>{attempt.problem_name}</strong>
                <MistakeBadge type={attempt.mistake_type} />
              </div>
              <p className="muted">
                {attempt.preferred_language} • {new Date(attempt.created_at).toLocaleString()}
              </p>
              <p>{attempt.generated_feedback}</p>
              <p className="note">Pattern: {attempt.repeated_pattern_notes}</p>
              <p className="note">Recommendation: {attempt.recommendation_notes}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}