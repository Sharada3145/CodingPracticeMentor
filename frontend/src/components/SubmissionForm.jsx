const languages = ["Python", "Java", "JavaScript", "C++"];

export default function SubmissionForm({
  form,
  problems,
  onChange,
  onToggleAutoDetect,
  onSubmit,
  submitting,
}) {
  const disabled = !form.student_name.trim() || !form.code_submission.trim();

  return (
    <section className="card">
      <h2>Submit Attempt</h2>
      <form onSubmit={onSubmit} className="form-grid">
        <label>
          Student Name
          <input
            name="student_name"
            value={form.student_name}
            onChange={onChange}
            placeholder="Aarav"
          />
        </label>

        <label>
          Preferred Language
          <select name="preferred_language" value={form.preferred_language} onChange={onChange}>
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            ))}
          </select>
        </label>

        <label>
          Problem
          <select
            name="problem_name"
            value={form.problem_name}
            onChange={onChange}
            disabled={form.auto_detect_problem}
          >
            {problems.map((problem) => (
              <option key={problem} value={problem}>
                {problem}
              </option>
            ))}
          </select>
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={form.auto_detect_problem}
            onChange={onToggleAutoDetect}
          />
          Auto-detect problem from code
        </label>

        <label className="full-width">
          Code Submission
          <textarea
            name="code_submission"
            value={form.code_submission}
            onChange={onChange}
            rows={10}
            placeholder="Paste code or mock code here..."
          />
        </label>

        <button type="submit" disabled={disabled || submitting} className="primary-btn">
          {submitting ? "Analyzing..." : "Submit Attempt"}
        </button>
      </form>
    </section>
  );
}