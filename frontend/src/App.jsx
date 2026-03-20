import { useEffect, useState } from "react";
import DashboardPanel from "./components/DashboardPanel";
import Header from "./components/Header";
import HistoryList from "./components/HistoryList";
import SubmissionForm from "./components/SubmissionForm";

const API_BASE = "https://codingpracticementor-2.onrender.com";

const defaultForm = {
  student_name: "",
  preferred_language: "Python",
  problem_name: "Two Sum",
  code_submission: "",
  auto_detect_problem: false,
};

function StatusCard({ latest }) {
  if (!latest) {
    return (
      <section className="card">
        <h2>Latest Feedback</h2>
        <p>Submit an attempt to see personalized coaching.</p>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>Latest Feedback</h2>
      <p>
        <span className={`badge ${latest.mistake_type}`}>{latest.mistake_type}</span>
      </p>
      <p>{latest.generated_feedback}</p>
      <p className="note">Pattern: {latest.repeated_pattern_notes}</p>
      <p className="note">Recommendation: {latest.recommendation_notes}</p>
    </section>
  );
}

export default function App() {
  const [form, setForm] = useState(defaultForm);
  const [problems, setProblems] = useState(["Two Sum"]);
  const [students, setStudents] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [attempts, setAttempts] = useState([]);
  const [latest, setLatest] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchProblems();
    fetchStudents();
  }, []);

  useEffect(() => {
    const student = form.student_name.trim();
    if (!student) {
      setDashboard(null);
      setAttempts([]);
      return;
    }
    refreshStudentData(student);
  }, [form.student_name]);

  async function fetchProblems() {
    const res = await fetch(`${API_BASE}/problems`);
    const data = await res.json();
    setProblems(data.problems || []);
    setForm((prev) => ({ ...prev, problem_name: data.problems?.[0] || "General Practice" }));
  }

  async function fetchStudents() {
    const res = await fetch(`${API_BASE}/students`);
    const data = await res.json();
    setStudents(data.students || []);
  }

  async function refreshStudentData(student) {
    const [dashRes, histRes] = await Promise.all([
      fetch(`${API_BASE}/dashboard/${encodeURIComponent(student)}`),
      fetch(`${API_BASE}/history/${encodeURIComponent(student)}`),
    ]);
    setDashboard(await dashRes.json());
    const history = await histRes.json();
    setAttempts(history.attempts || []);
    setLatest(history.attempts?.[0] || null);
  }

  function onChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  function onToggleAutoDetect() {
    setForm((prev) => ({ ...prev, auto_detect_problem: !prev.auto_detect_problem }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setMessage("");
    try {
      const payload = { ...form, student_name: form.student_name.trim() };
      const res = await fetch(`${API_BASE}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Submit failed with status ${res.status}`);
      }

      const data = await res.json();
      setLatest(data);
      await fetchStudents();
      await refreshStudentData(payload.student_name);
      setMessage("Submission saved and dashboard updated.");
    } catch (err) {
      setMessage(`Submit failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  }

  async function seed() {
    await fetch(`${API_BASE}/seed`, { method: "POST" });
    await fetchStudents();
    setMessage("Demo data seeded.");
  }

  async function reset() {
    await fetch(`${API_BASE}/reset`, { method: "POST" });
    setDashboard(null);
    setAttempts([]);
    setLatest(null);
    setForm(defaultForm);
    await fetchStudents();
    setMessage("Demo state reset.");
  }

  async function loadStudent(name) {
    setForm((prev) => ({ ...prev, student_name: name }));
    await refreshStudentData(name);
  }

  return (
    <main className="layout">
      <Header />

      <section className="card controls">
        <h2>Demo Controls</h2>
        <div className="control-row">
          <button onClick={seed}>Seed Demo Data</button>
          <button onClick={() => loadStudent("Aarav")}>Load Aarav</button>
          <button onClick={() => loadStudent("Maya")}>Load Maya</button>
          <button className="danger" onClick={reset}>
            Reset Demo State
          </button>
        </div>
        <p className="muted">Students in memory: {students.join(", ") || "none"}</p>
        {message ? <p className="note">{message}</p> : null}
      </section>

      <div className="grid-2">
        <SubmissionForm
          form={form}
          problems={problems}
          onChange={onChange}
          onToggleAutoDetect={onToggleAutoDetect}
          onSubmit={onSubmit}
          submitting={submitting}
        />
        <StatusCard latest={latest} />
      </div>

      <div className="grid-2">
        <DashboardPanel dashboard={dashboard} />
        <HistoryList attempts={attempts} />
      </div>
    </main>
  );
}
