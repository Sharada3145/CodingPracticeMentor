# AI Coding Practice Mentor

AI Coding Practice Mentor is a memory-aware learning coach dashboard for coding students.

Unlike generic coding judges, this MVP remembers student attempts and adapts coaching over time.

## Why this matters

Most coding practice tools treat each submission as isolated.
This project demonstrates a Hindsight-style loop:

- retain: store each attempt in SQLite
- recall: retrieve historical attempts per student
- learning: detect repeated mistakes and weak topics
- adaptation: generate personalized coaching and next-practice recommendations

## MVP capabilities

- Student memory fields:
  - student name
  - preferred language
  - problem name/topic
  - code submission
  - mistake/result type
  - generated feedback
  - repeated mistake pattern notes
  - recommendation notes
- Submission flow with language, problem, auto-detect option, and code input
- Rule-based mistake classification:
  - syntax_error
  - off_by_one
  - edge_case
  - wrong_logic
  - inefficient_solution
  - runtime_error
  - correct_solution
  - needs_test_validation
- Personalized coaching based on the student history
- Dashboard with:
  - preferred language
  - total attempts
  - repeated mistakes
  - strongest topic
  - weakest topic
  - next recommendation
  - attempt history
- Demo controls:
  - seed demo data
  - load demo student Aarav
  - load demo student Maya
  - reset demo state

## Demo narratives

- Aarav: repeated array off_by_one and edge_case patterns in Python
- Maya: repeated recursion wrong_logic patterns in Java

## Tech stack

- Frontend: React + Vite
- Backend: FastAPI
- Database: SQLite + SQLAlchemy

## Project structure

```
project-root/
  backend/
    main.py
    analysis.py
    evaluator.py
    database.py
    models.py
    seed.py
    requirements.txt
  frontend/
    package.json
    vite.config.js
    index.html
    src/
      main.jsx
      App.jsx
      styles.css
      components/
        Header.jsx
        SubmissionForm.jsx
        DashboardPanel.jsx
        HistoryList.jsx
  README.md
  .gitignore
```

## Run locally

### 1. Backend

From the repository root:

```bash
cd backend
python -m venv .venv
# Windows cmd
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at https://codingpracticementor-2.onrender.com

### 2. Frontend

Open a new terminal from repository root:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://127.0.0.1:5173

## 2-minute demo script

1. Start backend and frontend.
2. Click Seed Demo Data.
3. Click Load Aarav.
4. Show repeated mistakes and recommendation in dashboard/history.
5. Submit one new attempt for Aarav.
6. Show updated feedback and changed history count.
7. Click Load Maya and highlight recursion wrong_logic pattern.

## API endpoints

- GET /health
- GET /problems
- POST /submit
- GET /history/{user}
- GET /dashboard/{user}
- POST /seed
- POST /reset
- GET /students

## Future improvements

- Secure code sandboxing and isolated execution
- Better semantic code analysis (AST and test-case evaluation)
- Multi-user auth and classroom cohorts
- Richer learning plans with spaced repetition
- LLM-assisted hint generation grounded in student memory
