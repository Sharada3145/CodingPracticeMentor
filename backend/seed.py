from sqlalchemy.orm import Session

from analysis import generate_feedback
from models import Attempt


def seed_demo_data(db: Session):
    if db.query(Attempt).count() > 0:
        return {"message": "Seed skipped: database already has data.", "inserted": 0}

    rows = [
        {
            "student_name": "Aarav",
            "preferred_language": "Python",
            "problem_name": "Two Sum",
            "code_submission": "for i in range(len(nums)):\n    for j in range(i+1, len(nums)):\n        if nums[i] + nums[j] == target:\n            return [i, j]",
            "mistake_type": "off_by_one",
        },
        {
            "student_name": "Aarav",
            "preferred_language": "Python",
            "problem_name": "Binary Search",
            "code_submission": "while left < right:\n    mid = (left + right)//2\n    if arr[mid] == target:\n        return mid",
            "mistake_type": "edge_case",
        },
        {
            "student_name": "Aarav",
            "preferred_language": "Python",
            "problem_name": "Two Sum",
            "code_submission": "for i in range(len(nums)):\n    if nums[i+1] == target:\n        return i",
            "mistake_type": "off_by_one",
        },
        {
            "student_name": "Maya",
            "preferred_language": "Java",
            "problem_name": "Fibonacci Recursion",
            "code_submission": "int fib(int n){ return fib(n-1)+fib(n-2); }",
            "mistake_type": "wrong_logic",
        },
        {
            "student_name": "Maya",
            "preferred_language": "Java",
            "problem_name": "Fibonacci Recursion",
            "code_submission": "int fib(int n){ if(n==0)return 0; return fib(n-1)+fib(n-2); }",
            "mistake_type": "wrong_logic",
        },
        {
            "student_name": "Maya",
            "preferred_language": "Java",
            "problem_name": "Valid Parentheses",
            "code_submission": "public boolean isValid(String s){ return true; }",
            "mistake_type": "needs_test_validation",
        },
    ]

    inserted = 0
    for row in rows:
        history = db.query(Attempt).filter(Attempt.student_name == row["student_name"]).all()
        history_mistakes = [h.mistake_type for h in history]
        history_topics = [h.problem_name for h in history]

        feedback, repeated_note, recommendation = generate_feedback(
            student_name=row["student_name"],
            language=row["preferred_language"],
            problem_name=row["problem_name"],
            mistake_type=row["mistake_type"],
            history_mistakes=history_mistakes,
            history_topics=history_topics,
        )

        db.add(
            Attempt(
                student_name=row["student_name"],
                preferred_language=row["preferred_language"],
                problem_name=row["problem_name"],
                code_submission=row["code_submission"],
                mistake_type=row["mistake_type"],
                generated_feedback=feedback,
                repeated_pattern_notes=repeated_note,
                recommendation_notes=recommendation,
            )
        )
        db.commit()
        inserted += 1

    return {"message": "Seed complete.", "inserted": inserted}
