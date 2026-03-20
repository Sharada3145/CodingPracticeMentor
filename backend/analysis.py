from collections import Counter
from typing import List, Tuple

from evaluator import get_problem_hint, get_problem_topic


def detect_problem_from_code(code: str) -> str:
    lower = code.lower()
    if "fibonacci" in lower or "fib(" in lower:
        return "Fibonacci Recursion"
    if "binary" in lower and "search" in lower:
        return "Binary Search"
    if "parenth" in lower or "stack" in lower:
        return "Valid Parentheses"
    if "two sum" in lower or "target" in lower:
        return "Two Sum"
    if "reverse" in lower and "string" in lower:
        return "Reverse String"
    return "General Practice"


def classify_submission(code: str, language: str, problem_name: str) -> str:
    lower = code.lower()
    topic = get_problem_topic(problem_name)
    lang = language.lower()

    if not code.strip():
        return "needs_test_validation"
    if any(x in lower for x in ["syntaxerror", "unexpected token", "indentationerror", "missing ;"]):
        return "syntax_error"
    if any(x in lower for x in ["indexerror", "nullpointer", "exception", "traceback"]):
        return "runtime_error"
    if topic in {"arrays", "search", "strings"} and any(x in lower for x in ["<= len", "i <=", "j <=", "i+1", "j+1"]):
        return "off_by_one"
    if topic in {"arrays", "search", "strings"} and "if" not in lower:
        return "edge_case"
    if "for" in lower and lower.count("for") >= 2 and topic in {"arrays", "strings"}:
        return "inefficient_solution"
    if "todo" in lower or "pass" in lower:
        return "needs_test_validation"
    if lang == "java" and topic == "recursion" and "if (n <= 1)" not in lower:
        return "wrong_logic"
    if "return" in lower and ("for" in lower or "while" in lower):
        return "correct_solution"
    return "wrong_logic"


def _repeated_mistake_note(history_mistakes: List[str], current_mistake: str, topic: str, language: str) -> str:
    counts = Counter([m for m in history_mistakes if m != "correct_solution"])
    current_count = counts.get(current_mistake, 0)
    if current_mistake != "correct_solution" and current_count >= 2:
        return (
            f"Repeated pattern detected: {current_mistake} has appeared {current_count + 1} times "
            f"in {topic} practice using {language.title()}."
        )
    if counts:
        top, freq = counts.most_common(1)[0]
        return f"Most common historical struggle: {top} ({freq} prior attempts)."
    return "No repeated mistake pattern yet."


def _recommendation_note(history_topics: List[str], history_mistakes: List[str], current_topic: str) -> str:
    topic_counts = Counter(history_topics)
    mistake_counts = Counter([m for m in history_mistakes if m != "correct_solution"])

    weakest_topic = topic_counts.most_common(1)[0][0] if topic_counts else None
    repeated_mistake = mistake_counts.most_common(1)[0][0] if mistake_counts else None

    if weakest_topic and repeated_mistake:
        return (
            f"Next practice: focus on {weakest_topic}, specifically preventing {repeated_mistake}. "
            f"Start with boundary-driven tests before coding."
        )
    if current_topic != "general":
        return f"Next practice: 2 more {current_topic} problems with explicit edge-case checks first."
    return "Next practice: mix one arrays problem and one recursion problem with test-first thinking."


def generate_feedback(
    student_name: str,
    language: str,
    problem_name: str,
    mistake_type: str,
    history_mistakes: List[str],
    history_topics: List[str],
) -> Tuple[str, str, str]:
    topic = get_problem_topic(problem_name)

    base_feedback = {
        "syntax_error": "Syntax issue detected. Fix parser-level errors first, then rerun quickly.",
        "off_by_one": "Off-by-one signal detected. Recheck loop boundaries and index movement.",
        "edge_case": "Edge-case gap detected. Add tests for empty, single, and max-size inputs.",
        "wrong_logic": "Core logic drift detected. Walk through one small example line by line.",
        "inefficient_solution": "Solution works but seems inefficient. Consider hashing or two-pointer options.",
        "runtime_error": "Runtime failure likely. Add guards for null/empty values and index safety.",
        "correct_solution": "Great work. This attempt looks correct based on lightweight checks.",
        "needs_test_validation": "Incomplete signal. Add full code and test validation notes for better diagnosis.",
    }[mistake_type]

    repeated_note = _repeated_mistake_note(history_mistakes, mistake_type, topic, language)
    recommendation = _recommendation_note(history_topics + [topic], history_mistakes + [mistake_type], topic)
    hint = get_problem_hint(problem_name)

    feedback = (
        f"{base_feedback} {student_name}, you are currently practicing {topic} in {language.title()}. {hint}"
    )
    return feedback, repeated_note, recommendation
