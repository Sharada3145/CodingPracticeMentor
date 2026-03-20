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

    if re.search(r"^[ \t]*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*$", stripped, flags=re.MULTILINE):
        return True, "incomplete_assignment"

    if _has_unbalanced_pairs(stripped):
        return True, "unbalanced_brackets"

    selected = normalize_language(selected_language)
    if is_supported_problem(problem_name):
        if selected == "python" and "def " not in lower:
            return True, "missing_python_function"
        if selected == "python":
            control_starts = ("if ", "elif ", "else", "for ", "while ", "try", "except", "finally", "with ")

            # Catch a common syntax issue: missing ':' after function definition.
            for line in stripped.splitlines():
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith("#"):
                    continue

                if line_stripped.startswith("def ") and not line_stripped.endswith(":"):
                    return True, "missing_colon_in_def"

                if line_stripped.startswith(control_starts) and not line_stripped.endswith(":"):
                    return True, "missing_colon_in_control_statement"

            # Guard against common indentation problems in Python blocks.
            lines = stripped.splitlines()
            for index, line in enumerate(lines):
                if not line.strip() or line.lstrip().startswith("#"):
                    continue

                if "\t" in line:
                    return True, "invalid_indentation_tabs"

                indent = len(line) - len(line.lstrip(" "))
                if indent % 4 != 0:
                    return True, "invalid_indentation_width"

                if index > 0:
                    prev = lines[index - 1].strip()
                    if prev.endswith(":") and indent == 0:
                        return True, "invalid_indentation_after_block"
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
    mistake_type, _ = classify_submission_with_confidence(code, selected_language, problem_name)
    return mistake_type


def classify_submission_with_confidence(code: str, selected_language: str, problem_name: str) -> Tuple[str, str]:
    inferred_language, lang_conf = infer_language_from_code(code)
    mismatch, mismatch_conf = detect_language_mismatch(selected_language, inferred_language, lang_conf)

    malformed, _ = detect_malformed_code(code, selected_language, problem_name)
    if malformed:
        return "syntax_error", "medium"

    if mismatch:
        if mismatch_conf >= 0.65:
            return "syntax_error", "medium"
        return "needs_test_validation", "low"

    inferred_problem, inferred_problem_conf = infer_problem_from_code(code)
    selected_supported = is_supported_problem(problem_name)
    final_problem = problem_name if selected_supported else inferred_problem
    final_problem_conf = 0.9 if selected_supported else inferred_problem_conf

    if not is_supported_problem(final_problem):
        return "needs_test_validation", "low"

    allow, _ = should_allow_judging(
        selected_language=selected_language,
        inferred_language=inferred_language,
        language_confidence=lang_conf,
        problem_name=final_problem,
        problem_confidence=final_problem_conf,
        code=code,
    )
    if not allow:
        return "needs_test_validation", "low"

    result = evaluate_supported_submission(final_problem, selected_language, code)
    if result.get("passed"):
        return "correct_solution", "high"

    failure_type = result.get("failure_type") or "wrong_logic"
    if failure_type == "needs_test_validation":
        return failure_type, "low"
    return failure_type, "medium"


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

    target_topic = topic_counts.most_common(1)[0][0] if topic_counts else current_topic
    if not target_topic or target_topic == "general":
        target_topic = "array"

    repeated_mistake = mistake_counts.most_common(1)[0][0] if mistake_counts else None
    repeated_count = mistake_counts.get(repeated_mistake, 0) if repeated_mistake else 0

    focus_by_mistake = {
        "syntax_error": "syntax basics like colons, indentation, and balanced brackets",
        "off_by_one": "boundary checks and index movement",
        "edge_case": "edge-case coverage for empty, single, duplicate, and extreme inputs",
        "wrong_logic": "logic tracing, condition order, and early return conditions",
        "inefficient_solution": "time complexity, hash-map usage, and avoiding nested loops",
        "runtime_error": "null/empty guards and safe condition checks",
        "needs_test_validation": "complete function structure and explicit expected-output tests",
    }

    if repeated_mistake in focus_by_mistake:
        focus = focus_by_mistake[repeated_mistake]
        problems_to_solve = 3 if repeated_count >= 3 else 2
    else:
        focus = "boundary checks and early return conditions"
        problems_to_solve = 2

    topic_label = target_topic[:-1] if target_topic.endswith("s") else target_topic
    return (
        f"Practice {problems_to_solve} {topic_label} problems focusing on {focus}."
    )


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

    mistake_explanations: Dict[str, str] = {
        "syntax_error": (
            "Explanation: Some required syntax is missing or invalid, such as a missing ':' in Python "
            "or unmatched brackets."
        ),
        "off_by_one": (
            "Explanation: The loop or pointer moves one step too far or stops one step too early, "
            "which skips the correct index."
        ),
        "wrong_logic": (
            "Explanation: The steps are valid Python/Java syntax, but the algorithm decision path is "
            "not matching the problem rule."
        ),
        "edge_case": (
            "Explanation: Main examples may pass, but special inputs like empty lists, one element, "
            "duplicates, or extremes are not handled yet."
        ),
    }

    quick_fix_suggestions: Dict[str, str] = {
        "off_by_one": (
            "Quick fix: Use `for i in range(len(nums))` or `while left <= right`, and update indexes with `+1`/`-1` exactly once per step."
        ),
        "syntax_error": (
            "Quick fix: Add missing `:` after block headers, close brackets/parentheses, and ensure assignments have a value (for example `x = 0`)."
        ),
        "wrong_logic": (
            "Quick fix: Follow the problem hint step-by-step and trace one small example to verify each condition and return path."
        ),
    }

    explanation = mistake_explanations.get(mistake_type, "")
    explanation_part = f" {explanation}" if explanation else ""
    quick_fix = quick_fix_suggestions.get(mistake_type, "")
    quick_fix_part = f" {quick_fix}" if quick_fix else ""

    feedback = (
        f"{base_feedback[mistake_type]}{explanation_part} "
        f"{student_name}, current track: {topic} in {normalized_language}.{quick_fix_part} "
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


def detect_learning_trend(records: List[object]) -> str:
    if len(records) < 4:
        return "insufficient_data"

    last_three = records[-3:]
    previous = records[:-3]

    last_three_mistakes = [r.mistake_type for r in last_three if r.mistake_type != "correct_solution"]
    previous_mistakes = [r.mistake_type for r in previous if r.mistake_type != "correct_solution"]

    # Same mistake repeated across the recent 3 attempts indicates stagnation.
    if len(last_three_mistakes) == 3 and len(set(last_three_mistakes)) == 1:
        return "stagnating"

    recent_error_count = len(last_three_mistakes)
    previous_error_rate = len(previous_mistakes) / len(previous) if previous else 0.0
    previous_baseline_for_three = previous_error_rate * 3

    if recent_error_count < previous_baseline_for_three:
        return "improving"
    if recent_error_count > previous_baseline_for_three:
        return "declining"
    return "stagnating"
