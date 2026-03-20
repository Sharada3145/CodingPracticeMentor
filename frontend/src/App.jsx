import { useEffect, useMemo, useState } from "react";
import DashboardPanel from "./components/DashboardPanel";
import Header from "./components/Header";
import HistoryList from "./components/HistoryList";
import SubmissionForm from "./components/SubmissionForm";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

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
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState("");

  const selectedStudent = useMemo(() => form.student_name.trim(), [form.student_name]);

  useEffect(() => {
    fetchProblems();
    fetchStudents();
  }, []);

  useEffect(() => {
    if (selectedStudent) {
      refreshStudentData(selectedStudent);
    }
  }, [selectedStudent]);

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
    setLoading(true);
    try {
      const [dashRes, historyRes] = await Promise.all([
        fetch(`${API_BASE}/dashboard/${encodeURIComponent(student)}`),
        fetch(`${API_BASE}/history/${encodeURIComponent(student)}`),
      ]);
      const dash = await dashRes.json();
      const hist = await historyRes.json();
      setDashboard(dash);
      setAttempts(hist.attempts || []);
      setLatest(hist.attempts?.[0] || null);
    } finally {
      setLoading(false);
    }
  }

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleToggleAutoDetect() {
    setForm((prev) => ({ ...prev, auto_detect_problem: !prev.auto_detect_problem }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        student_name: form.student_name.trim(),
      };
      const res = await fetch(`${API_BASE}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      setLatest(data);
      setToast("Attempt stored and coaching updated.");
      await fetchStudents();
      if (payload.student_name) {
        await refreshStudentData(payload.student_name);
      }
    } catch (err) {
      setToast("Submission failed. Confirm backend is running.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSeed() {
    await fetch(`${API_BASE}/seed`, { method: "POST" });
    await fetchStudents();
    setToast("Demo data seeded.");
  }

  async function handleReset() {
    await fetch(`${API_BASE}/reset`, { method: "POST" });
    setDashboard(null);
    setAttempts([]);
    setLatest(null);
    setForm(defaultForm);
    await fetchStudents();
    setToast("Demo state reset.");
  }

  async function loadDemoStudent(name) {
    setForm((prev) => ({ ...prev, student_name: name }));
    await refreshStudentData(name);
    setToast(`Loaded demo student ${name}.`);
  }

  return (
    <main className="layout">
      <Header />

      <section className="card controls">
        <h2>Demo Controls</h2>
        <div className="control-row">
          <button onClick={handleSeed}>Seed Demo Data</button>
          <button onClick={() => loadDemoStudent("Aarav")}>Load Aarav</button>
          <button onClick={() => loadDemoStudent("Maya")}>Load Maya</button>
          <button className="danger" onClick={handleReset}>
            Reset Demo State
          </button>
        </div>
        <p className="muted">Students in memory: {students.join(", ") || "none"}</p>
      </section>

      {toast && <p className="toast">{toast}</p>}

      <div className="grid-2">
        <SubmissionForm
          form={form}
          problems={problems}
          onChange={handleChange}
          onToggleAutoDetect={handleToggleAutoDetect}
          onSubmit={handleSubmit}
          submitting={submitting}
        />
        <StatusCard latest={latest} />
      </div>

      <div className="grid-2">
        <DashboardPanel dashboard={dashboard} />
        <HistoryList attempts={attempts} />
      </div>

      {loading && <p className="muted">Refreshing student memory...</p>}
    </main>
  );
}