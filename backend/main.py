from collections import Counter, defaultdict
from typing import List, Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from analysis import classify_submission, detect_problem_from_code, generate_feedback
from database import Base, engine, get_db
from models import Attempt
from seed import seed_demo_data

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Coding Practice Mentor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROBLEMS = [
    "Two Sum",
    "Binary Search",
    "Reverse String",
    "Fibonacci Recursion",
    "Valid Parentheses",
    "General Practice",
]


class SubmitRequest(BaseModel):
    student_name: str
    preferred_language: str
    problem_name: Optional[str] = None
    code_submission: str
    auto_detect_problem: bool = False


class SubmitResponse(BaseModel):
    id: int
    student_name: str
    preferred_language: str
    problem_name: str
    mistake_type: str
    generated_feedback: str
    repeated_pattern_notes: str
    recommendation_notes: str


@app.get("/health")
def health():
    return {"status": "ok", "message": "AI Coding Practice Mentor backend is running."}


@app.get("/problems")
def list_problems():
    return {"problems": PROBLEMS}


@app.get("/students")
def list_students(db: Session = Depends(get_db)):
    students = [
        row[0]
        for row in db.query(Attempt.student_name)
        .distinct()
        .order_by(func.lower(Attempt.student_name).asc())
        .all()
    ]
    return {"students": students}


@app.post("/submit", response_model=SubmitResponse)
def submit_attempt(payload: SubmitRequest, db: Session = Depends(get_db)):
    student_name = payload.student_name.strip()
    preferred_language = payload.preferred_language.strip()
    problem_name = payload.problem_name.strip() if payload.problem_name else ""

    if payload.auto_detect_problem or not problem_name:
        problem_name = detect_problem_from_code(payload.code_submission)

    mistake_type = classify_submission(payload.code_submission, preferred_language, problem_name)

    history = (
        db.query(Attempt)
        .filter(Attempt.student_name == student_name)
        .order_by(Attempt.created_at.asc())
        .all()
    )
    history_mistakes = [h.mistake_type for h in history]
    history_topics = [h.problem_name for h in history]

    generated_feedback, repeated_pattern_notes, recommendation_notes = generate_feedback(
        student_name=student_name,
        language=preferred_language,
        problem_name=problem_name,
        mistake_type=mistake_type,
        history_mistakes=history_mistakes,
        history_topics=history_topics,
    )

    attempt = Attempt(
        student_name=student_name,
        preferred_language=preferred_language,
        problem_name=problem_name,
        code_submission=payload.code_submission,
        mistake_type=mistake_type,
        generated_feedback=generated_feedback,
        repeated_pattern_notes=repeated_pattern_notes,
        recommendation_notes=recommendation_notes,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return SubmitResponse(
        id=attempt.id,
        student_name=attempt.student_name,
        preferred_language=attempt.preferred_language,
        problem_name=attempt.problem_name,
        mistake_type=attempt.mistake_type,
        generated_feedback=attempt.generated_feedback,
        repeated_pattern_notes=attempt.repeated_pattern_notes,
        recommendation_notes=attempt.recommendation_notes,
    )


@app.get("/history/{user}")
def get_history(user: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Attempt)
        .filter(Attempt.student_name == user)
        .order_by(Attempt.created_at.desc())
        .all()
    )
    return {
        "student": user,
        "attempts": [
            {
                "id": r.id,
                "preferred_language": r.preferred_language,
                "problem_name": r.problem_name,
                "mistake_type": r.mistake_type,
                "generated_feedback": r.generated_feedback,
                "repeated_pattern_notes": r.repeated_pattern_notes,
                "recommendation_notes": r.recommendation_notes,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ],
    }


@app.get("/dashboard/{user}")
def get_dashboard(user: str, db: Session = Depends(get_db)):
    records: List[Attempt] = (
        db.query(Attempt)
        .filter(Attempt.student_name == user)
        .order_by(Attempt.created_at.asc())
        .all()
    )

    if not records:
        return {
            "student": user,
            "preferred_language": "-",
            "total_attempts": 0,
            "repeated_mistakes": [],
            "strongest_topic": "-",
            "weakest_topic": "-",
            "next_recommendation": "Submit an attempt to get personalized coaching.",
            "last_feedback": "No attempts yet.",
        }

    language_counts = Counter([r.preferred_language for r in records])
    preferred_language = language_counts.most_common(1)[0][0]

    mistake_counts = Counter([r.mistake_type for r in records if r.mistake_type != "correct_solution"])
    repeated_mistakes = [
        {"mistake": mistake, "count": count}
        for mistake, count in mistake_counts.items()
        if count >= 2
    ]

    topic_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    for r in records:
        topic_stats[r.problem_name]["total"] += 1
        if r.mistake_type == "correct_solution":
            topic_stats[r.problem_name]["correct"] += 1

    scored = []
    for topic, stats in topic_stats.items():
        ratio = stats["correct"] / stats["total"] if stats["total"] else 0
        scored.append((topic, ratio, stats["total"]))

    strongest_topic = sorted(scored, key=lambda x: (-x[1], -x[2], x[0]))[0][0]
    weakest_topic = sorted(scored, key=lambda x: (x[1], -x[2], x[0]))[0][0]
    latest = records[-1]

    return {
        "student": user,
        "preferred_language": preferred_language,
        "total_attempts": len(records),
        "repeated_mistakes": repeated_mistakes,
        "strongest_topic": strongest_topic,
        "weakest_topic": weakest_topic,
        "next_recommendation": latest.recommendation_notes,
        "last_feedback": latest.generated_feedback,
    }


@app.post("/seed")
def seed(db: Session = Depends(get_db)):
    return seed_demo_data(db)


@app.post("/reset")
def reset(db: Session = Depends(get_db)):
    db.query(Attempt).delete()
    db.commit()
    return {"message": "Demo state reset complete."}
