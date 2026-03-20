function MistakePill({ type }) {
  return <span className={`badge ${type}`}>{type}</span>;
}

function TrendLabel({ trend }) {
  const value = trend || "insufficient_data";
  const textMap = {
    improving: "improving",
    stagnating: "stagnating",
    declining: "declining",
    insufficient_data: "insufficient data",
  };

  return <span className={`trend-badge ${value}`}>{textMap[value] || value}</span>;
}

export default function DashboardPanel({ dashboard, attempts = [] }) {
  if (!dashboard) {
    return (
      <section className="card">
        <h2>Learning Dashboard</h2>
        <p>No student selected yet.</p>
      </section>
    );
  }

  const mistakeCounts = attempts.reduce((acc, attempt) => {
    if (attempt.mistake_type === "correct_solution") return acc;
    acc[attempt.mistake_type] = (acc[attempt.mistake_type] || 0) + 1;
    return acc;
  }, {});

  const chartRows = Object.entries(mistakeCounts).sort((a, b) => b[1] - a[1]);
  const maxCount = chartRows.length ? chartRows[0][1] : 1;

  return (
    <section className="card">
      <h2>Learning Dashboard</h2>
      <div className="quick-stats-grid">
        <div className="stat-card">
          <p className="muted">Preferred Language</p>
          <strong>{dashboard.preferred_language}</strong>
        </div>
        <div className="stat-card">
          <p className="muted">Total Attempts</p>
          <strong>{dashboard.total_attempts}</strong>
        </div>
        <div className="stat-card">
          <p className="muted">Strongest Topic</p>
          <strong>{dashboard.strongest_topic}</strong>
        </div>
        <div className="stat-card">
          <p className="muted">Weakest Topic</p>
          <strong>{dashboard.weakest_topic}</strong>
        </div>
        <div className="stat-card">
          <p className="muted">Learning Trend</p>
          <TrendLabel trend={dashboard.learning_trend} />
        </div>
        <div className="stat-card stat-card-wide">
          <p className="muted">Next Recommendation</p>
          <strong className="recommendation-text">{dashboard.next_recommendation}</strong>
        </div>
      </div>

      <div className="dashboard-section">
        <p className="muted">Repeated Mistakes</p>
        {dashboard.repeated_mistakes?.length ? (
          <div className="pill-row">
            {dashboard.repeated_mistakes.map((item) => (
              <div key={item.mistake} className="mistake-chip">
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
        <p className="muted">Mistake Breakdown</p>
        {chartRows.length ? (
          <div className="mistake-chart">
            {chartRows.map(([mistake, count]) => (
              <div key={mistake} className="chart-row">
                <span className="chart-label">{mistake}</span>
                <div className="chart-track">
                  <div
                    className={`chart-fill ${mistake}`}
                    style={{ width: `${Math.max((count / maxCount) * 100, 8)}%` }}
                  />
                </div>
                <span className="chart-value">{count}</span>
              </div>
            ))}
          </div>
        ) : (
          <p>No mistakes to visualize yet.</p>
        )}
      </div>
    </section>
  );
}