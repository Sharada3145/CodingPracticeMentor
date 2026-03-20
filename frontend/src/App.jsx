import { useEffect, useState } from "react";
import DashboardPanel from "./components/DashboardPanel";
import Header from "./components/Header";
import HistoryList from "./components/HistoryList";
import SubmissionForm from "./components/SubmissionForm";

const BASE_URL = "https://codingpracticementor-2.onrender.com";

async function apiRequest(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || `Request failed (${res.status})`);
  }

  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return null;
}

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
    try {
      const data = await apiRequest("/problems");
      setProblems(data?.problems || []);
      setForm((prev) => ({ ...prev, problem_name: data?.problems?.[0] || "General Practice" }));
    } catch (err) {
      console.error("Failed to fetch problems:", err);
      setMessage("Could not load problems from server.");
    }
  }

  async function fetchStudents() {
    try {
      const data = await apiRequest("/students");
      setStudents(data?.students || []);
    } catch (err) {
      console.error("Failed to fetch students:", err);
      setMessage("Could not load student list.");
    }
  }

  async function refreshStudentData(student) {
    try {
      const [dashboardData, history] = await Promise.all([
        apiRequest(`/dashboard/${encodeURIComponent(student)}`),
        apiRequest(`/history/${encodeURIComponent(student)}`),
      ]);
      setDashboard(dashboardData || null);
      setAttempts(history?.attempts || []);
      setLatest(history?.attempts?.[0] || null);
    } catch (err) {
      console.error("Failed to refresh student data:", err);
      setMessage("Could not load dashboard/history for selected student.");
    }
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
      const data = await apiRequest("/submit", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setLatest(data);
      await fetchStudents();
      await refreshStudentData(payload.student_name);
      setMessage("Submission saved and dashboard updated.");
    } catch (err) {
      console.error("Submit failed:", err);
      setMessage(`Submit failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  }

  async function seed() {
    try {
      await apiRequest("/seed", { method: "POST" });
      await fetchStudents();
      setMessage("Demo data seeded.");
    } catch (err) {
      console.error("Seed failed:", err);
      setMessage("Seed failed. Check backend availability.");
    }
  }

  async function reset() {
    try {
      await apiRequest("/reset", { method: "POST" });
      setDashboard(null);
      setAttempts([]);
      setLatest(null);
      setForm(defaultForm);
      await fetchStudents();
      setMessage("Demo state reset.");
    } catch (err) {
      console.error("Reset failed:", err);
      setMessage("Reset failed. Check backend availability.");
    }
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
