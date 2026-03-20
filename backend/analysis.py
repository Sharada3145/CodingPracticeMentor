import re
from collections import Counter
from typing import Dict, List, Tuple

from evaluator import (
    evaluate_supported_submission,
    get_problem_hint,
    get_problem_topic,
    has_expected_structure,
    is_supported_problem,
    normalize_language,
)


def infer_language_from_code(code: str) -> Tuple[str, float]:
    lower = code.lower()
    python_markers = ["def ", "import ", "print(", " in range(", "elif ", "none", ":\n"]
    java_markers = ["public class", "class solution", "public static", "new int[]", "hashmap<", "boolean ", ";\n"]

    py_score = sum(1 for marker in python_markers if marker in lower)
    java_score = sum(1 for marker in java_markers if marker in lower)

    if py_score == 0 and java_score == 0:
        return "unknown", 0.0

    total = py_score + java_score
    if py_score > java_score:
        return "python", py_score / total
    if java_score > py_score:
        return "java", java_score / total
    return "unknown", 0.4


def detect_language_mismatch(selected_language: str, inferred_language: str, confidence: float) -> Tuple[bool, float]:
    selected = normalize_language(selected_language)
    inferred = normalize_language(inferred_language)

    if selected not in {"python", "java"}:
        return False, 0.0
    if inferred == "unknown":
        return False, 0.0
    if selected == inferred:
        return False, 0.0
    return True, confidence


def _has_unbalanced_pairs(code: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    opening = set(pairs.values())
    stack: List[str] = []

    for ch in code:
        if ch in opening:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return True
            stack.pop()

    return len(stack) > 0


def detect_malformed_code(code: str, selected_language: str, problem_name: str) -> Tuple[bool, str]:
    stripped = code.strip()
    lower = stripped.lower()

    if not stripped:
        return True, "empty_submission"

    non_empty_lines = [line for line in stripped.splitlines() if line.strip()]
    if len(non_empty_lines) < 2 or len(stripped) < 15:
        return True, "too_short"

    if _has_unbalanced_pairs(stripped):
        return True, "unbalanced_brackets"

    selected = normalize_language(selected_language)
    if is_supported_problem(problem_name):
        if selected == "python" and "def " not in lower:
            return True, "missing_python_function"
        if selected == "python":
            # Catch a common syntax issue: missing ':' after function definition.
            for line in stripped.splitlines():
                line_stripped = line.strip()
                if line_stripped.startswith("def ") and not line_stripped.endswith(":"):
                    return True, "missing_colon_in_def"
        if selected == "java" and "class solution" not in lower:
            return True, "missing_solution_class"

    return False, "ok"


def infer_problem_from_code(code: str) -> Tuple[str, float]:
    lower = code.lower()

    if "twosum" in lower or ("target" in lower and any(k in lower for k in ["hashmap", "seen"])):
        return "Two Sum", 0.85
    if "binary" in lower and "search" in lower:
        return "Binary Search", 0.85
    if "reverse" in lower and "string" in lower:
        return "Reverse String", 0.8
    if "fib(" in lower or "fibonacci" in lower:
        return "Fibonacci Recursion", 0.8
    if "parentheses" in lower or "stack" in lower:
        return "Valid Parentheses", 0.75

    return "General Practice", 0.2


def detect_problem_from_code(code: str) -> str:
    problem, _ = infer_problem_from_code(code)
    return problem


def should_allow_judging(
    selected_language: str,
    inferred_language: str,
    language_confidence: float,
    problem_name: str,
    problem_confidence: float,
    code: str,
) -> Tuple[bool, str]:
    selected = normalize_language(selected_language)
    inferred = normalize_language(inferred_language)

    if selected not in {"python", "java"}:
        return False, "unsupported_selected_language"
    if inferred != selected:
        return False, "language_mismatch"
    if language_confidence < 0.55:
        return False, "language_confidence_too_low"
    if not is_supported_problem(problem_name):
        return False, "unsupported_problem"
    if problem_confidence < 0.6:
        return False, "problem_confidence_too_low"

    structure_ok, reason = has_expected_structure(problem_name, selected, code)
    if not structure_ok:
        return False, reason

    return True, "ok"


def classify_submission(code: str, selected_language: str, problem_name: str) -> str:
    inferred_language, lang_conf = infer_language_from_code(code)
    mismatch, mismatch_conf = detect_language_mismatch(selected_language, inferred_language, lang_conf)

    malformed, _ = detect_malformed_code(code, selected_language, problem_name)
    if malformed:
        return "syntax_error"

    if mismatch:
        return "syntax_error" if mismatch_conf >= 0.65 else "needs_test_validation"

    inferred_problem, inferred_problem_conf = infer_problem_from_code(code)
    selected_supported = is_supported_problem(problem_name)
    final_problem = problem_name if selected_supported else inferred_problem
    final_problem_conf = 0.9 if selected_supported else inferred_problem_conf

    if not is_supported_problem(final_problem):
        return "needs_test_validation"

    allow, _ = should_allow_judging(
        selected_language=selected_language,
        inferred_language=inferred_language,
        language_confidence=lang_conf,
        problem_name=final_problem,
        problem_confidence=final_problem_conf,
        code=code,
    )
    if not allow:
        return "needs_test_validation"

    result = evaluate_supported_submission(final_problem, selected_language, code)
    if result.get("passed"):
        return "correct_solution"
    return result.get("failure_type") or "wrong_logic"


def _repeated_mistake_note(history_mistakes: List[str], current_mistake: str, topic: str, language: str) -> str:
    counts = Counter([m for m in history_mistakes if m != "correct_solution"])
    current_count = counts.get(current_mistake, 0)
    if current_mistake != "correct_solution" and current_count >= 2:
        return (
            f"Repeated pattern: {current_mistake} has appeared {current_count + 1} times "
            f"in {topic} ({language.title()})."
        )
    if counts:
        top, freq = counts.most_common(1)[0]
        return f"Top historical struggle: {top} ({freq} prior attempts)."
    return "No repeated mistake pattern yet."


def _recommendation_note(history_topics: List[str], history_mistakes: List[str], current_topic: str) -> str:
    topic_counts = Counter(history_topics)
    mistake_counts = Counter([m for m in history_mistakes if m != "correct_solution"])

    weakest_topic = topic_counts.most_common(1)[0][0] if topic_counts else None
    repeated_mistake = mistake_counts.most_common(1)[0][0] if mistake_counts else None

    if repeated_mistake and weakest_topic:
        return f"Next focus: {weakest_topic}. Practice specifically to reduce {repeated_mistake} mistakes."
    if current_topic != "general":
        return f"Next focus: two more {current_topic} tasks with explicit test cases before coding."
    return "Next focus: one arrays task and one recursion task with test-first workflow."


def generate_feedback(
    student_name: str,
    language: str,
    problem_name: str,
    mistake_type: str,
    history_mistakes: List[str],
    history_topics: List[str],
) -> Tuple[str, str, str]:
    topic = get_problem_topic(problem_name)
    normalized_language = normalize_language(language).title()

    correct_lines = {
        "arrays": "Solid result. This solution passes the mentor's checks for this arrays task.",
        "search": "Solid result. Search boundaries and transitions look correct.",
        "strings": "Solid result. String transformation flow looks correct.",
        "recursion": "Solid result. Recursion and base-case handling look correct.",
        "stacks": "Solid result. Stack validation behavior looks correct.",
        "general": "Solid result. This submission passes the current checks.",
    }

    base_feedback: Dict[str, str] = {
        "syntax_error": "The submission looks malformed or language-mismatched. Fix structure/syntax first.",
        "off_by_one": "Boundary handling appears off. Recheck indices and loop limits.",
        "edge_case": "Edge-case handling seems incomplete. Add empty/single/extreme input tests.",
        "wrong_logic": "Logic still diverges from expected behavior. Trace with a small example.",
        "inefficient_solution": "Approach looks too slow for larger inputs. Consider a more efficient strategy.",
        "runtime_error": "Potential runtime failure detected. Add guard checks and safer conditions.",
        "correct_solution": correct_lines.get(topic, correct_lines["general"]),
        "needs_test_validation": (
            "The mentor cannot fully verify this submission yet. "
            "Provide complete, well-structured code for a supported problem."
        ),
    }

    feedback = (
        f"{base_feedback[mistake_type]} {student_name}, current track: {topic} in {normalized_language}. "
        f"{get_problem_hint(problem_name)}"
    )

    repeated_note = _repeated_mistake_note(history_mistakes, mistake_type, topic, normalized_language)
    recommendation = _recommendation_note(history_topics + [topic], history_mistakes + [mistake_type], topic)
    return feedback, repeated_note, recommendation


def compute_topic_strengths(records: List[object]) -> Tuple[str, str]:
    stats: Dict[str, Dict[str, int]] = {}
    for record in records:
        topic = record.problem_name
        if topic not in stats:
            stats[topic] = {"correct": 0, "errors": 0, "total": 0}
        stats[topic]["total"] += 1
        if record.mistake_type == "correct_solution":
            stats[topic]["correct"] += 1
        else:
            stats[topic]["errors"] += 1

    enough_data = [topic for topic, s in stats.items() if s["total"] >= 2]
    if len(enough_data) == 0:
        return "N/A", "N/A"
    if len(enough_data) == 1:
        only = enough_data[0]
        return only, only

    scored = []
    for topic in enough_data:
        s = stats[topic]
        success_rate = s["correct"] / s["total"]
        mistake_concentration = s["errors"] / s["total"]
        scored.append((topic, success_rate, mistake_concentration, s["total"]))

    strongest = sorted(scored, key=lambda x: (-x[1], x[2], -x[3], x[0]))[0][0]
    weakest = sorted(scored, key=lambda x: (-x[2], x[1], -x[3], x[0]))[0][0]

    if strongest == weakest:
        candidates = [
            x[0]
            for x in sorted(scored, key=lambda x: (-x[2], x[1], -x[3], x[0]))
            if x[0] != strongest
        ]
        weakest = candidates[0] if candidates else weakest

    return strongest, weakest
