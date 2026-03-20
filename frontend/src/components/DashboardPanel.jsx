function MistakePill({ type }) {
  return <span className={`badge ${type}`}>{type}</span>;
}

export default function DashboardPanel({ dashboard }) {
  if (!dashboard) {
    return (
      <section className="card">
        <h2>Learning Dashboard</h2>
        <p>No student selected yet.</p>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>Learning Dashboard</h2>
      <div className="stats-grid">
        <div>
          <p className="muted">Preferred Language</p>
          <strong>{dashboard.preferred_language}</strong>
        </div>
        <div>
          <p className="muted">Total Attempts</p>
          <strong>{dashboard.total_attempts}</strong>
        </div>
        <div>
          <p className="muted">Strongest Topic</p>
          <strong>{dashboard.strongest_topic}</strong>
        </div>
        <div>
          <p className="muted">Weakest Topic</p>
          <strong>{dashboard.weakest_topic}</strong>
        </div>
      </div>

      <div className="dashboard-section">
        <p className="muted">Repeated Mistakes</p>
        {dashboard.repeated_mistakes?.length ? (
          <div className="pill-row">
            {dashboard.repeated_mistakes.map((item) => (
              <div key={item.mistake} className="mistake-item">
                <MistakePill type={item.mistake} />
                <span>x{item.count}</span>
              </div>
            ))}
          </div>
        ) : (
          <p>None detected yet.</p>
        )}
      </div>

      <div className="dashboard-section">
        <p className="muted">Next Recommendation</p>
        <p>{dashboard.next_recommendation}</p>
      </div>
    </section>
  );
}