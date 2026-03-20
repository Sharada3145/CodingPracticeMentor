from typing import Dict, List, Tuple

SUPPORTED_PROBLEMS: Dict[str, Dict[str, str]] = {
    "Two Sum": {
        "topic": "arrays",
        "hint": "Use complement lookup and return as soon as the pair is found.",
    },
    "Binary Search": {
        "topic": "search",
        "hint": "Keep left/right updates consistent and stop safely.",
    },
    "Reverse String": {
        "topic": "strings",
        "hint": "Use two pointers and stop when they cross.",
    },
    "Fibonacci Recursion": {
        "topic": "recursion",
        "hint": "Define complete base cases before recursion.",
    },
    "Valid Parentheses": {
        "topic": "stacks",
        "hint": "Push opens, validate closes, and ensure final stack is empty.",
    },
}


def normalize_language(language: str) -> str:
    raw = (language or "").strip().lower()
    if raw in {"py", "python"}:
        return "python"
    if raw == "java":
        return "java"
    return raw


def get_supported_problems() -> List[str]:
    return list(SUPPORTED_PROBLEMS.keys())


def is_supported_problem(problem_name: str) -> bool:
    return problem_name in SUPPORTED_PROBLEMS


def get_problem_topic(problem_name: str) -> str:
    if problem_name in SUPPORTED_PROBLEMS:
        return SUPPORTED_PROBLEMS[problem_name]["topic"]
    return "general"


def get_problem_hint(problem_name: str) -> str:
    if problem_name in SUPPORTED_PROBLEMS:
        return SUPPORTED_PROBLEMS[problem_name]["hint"]
    return "This problem is not fully supported yet; include tests and expected output."


def _has_python_signature(problem_name: str, code_lower: str) -> bool:
    signatures = {
        "Two Sum": ["def twosum("],
        "Binary Search": ["def binarysearch(", "def search("],
        "Reverse String": ["def reversestring(", "def reverse_string("],
        "Fibonacci Recursion": ["def fib("],
        "Valid Parentheses": ["def isvalid(", "def is_valid("],
    }
    return any(sig in code_lower for sig in signatures.get(problem_name, []))


def _has_java_signature(problem_name: str, code_lower: str) -> bool:
    signatures = {
        "Two Sum": ["int[] twosum("],
        "Binary Search": ["int search(", "int binarysearch("],
        "Reverse String": ["void reversestring(", "string reversestring("],
        "Fibonacci Recursion": ["int fib("],
        "Valid Parentheses": ["boolean isvalid("],
    }
    has_solution_class = "class solution" in code_lower
    return has_solution_class and any(sig in code_lower for sig in signatures.get(problem_name, []))


def has_expected_structure(problem_name: str, language: str, code: str) -> Tuple[bool, str]:
    code_lower = code.lower()
    normalized = normalize_language(language)

    if not is_supported_problem(problem_name):
        return False, "unsupported_problem"

    if normalized == "python":
        if not _has_python_signature(problem_name, code_lower):
            return False, "missing_python_signature"
        return True, "ok"

    if normalized == "java":
        if not _has_java_signature(problem_name, code_lower):
            return False, "missing_java_signature"
        return True, "ok"

    return False, "unsupported_language"


def evaluate_supported_submission(problem_name: str, language: str, code: str) -> Dict[str, object]:
    code_lower = code.lower()
    normalized = normalize_language(language)

    structure_ok, structure_reason = has_expected_structure(problem_name, normalized, code)
    if not structure_ok:
        return {"passed": False, "failure_type": "needs_test_validation", "reason": structure_reason}

    if "todo" in code_lower or "pass" in code_lower:
        return {"passed": False, "failure_type": "needs_test_validation", "reason": "placeholder_code"}

    if problem_name == "Two Sum":
        if normalized == "python":
            has_map = "{}" in code_lower or "dict(" in code_lower
            has_lookup = " in " in code_lower and "=" in code_lower
            has_return = "return [" in code_lower or "return(" in code_lower
            if has_map and has_lookup and has_return:
                return {"passed": True, "failure_type": "", "reason": "pass"}
            if code_lower.count("for ") >= 2:
                return {"passed": False, "failure_type": "inefficient_solution", "reason": "nested_loops"}
            return {"passed": False, "failure_type": "wrong_logic", "reason": "missing_complement_logic"}

        has_map = "hashmap" in code_lower or "map<" in code_lower
        has_lookup = ".containskey(" in code_lower or ".get(" in code_lower
        has_return = "return new int[]" in code_lower or "return new int[2]" in code_lower
        if has_map and has_lookup and has_return:
            return {"passed": True, "failure_type": "", "reason": "pass"}
        if code_lower.count("for(") >= 2 or code_lower.count("for (") >= 2:
            return {"passed": False, "failure_type": "inefficient_solution", "reason": "nested_loops"}
        return {"passed": False, "failure_type": "wrong_logic", "reason": "missing_complement_logic"}

    if problem_name == "Binary Search":
        core = all(k in code_lower for k in ["while", "mid", "left", "right", "return"])
        has_moves = any(
            k in code_lower
            for k in ["left = mid + 1", "right = mid - 1", "left=mid+1", "right=mid-1"]
        )
        if core and has_moves:
            return {"passed": True, "failure_type": "", "reason": "pass"}
        if core and not has_moves:
            return {"passed": False, "failure_type": "off_by_one", "reason": "boundary_update_missing"}
        return {"passed": False, "failure_type": "wrong_logic", "reason": "binary_search_incomplete"}

    if problem_name == "Reverse String":
        has_pointers = any(k in code_lower for k in ["left", "right", "i", "j"])
        has_swap = any(k in code_lower for k in ["swap", "temp", "="])
        has_loop = "while" in code_lower or "for" in code_lower
        if has_pointers and has_swap and has_loop:
            return {"passed": True, "failure_type": "", "reason": "pass"}
        return {"passed": False, "failure_type": "wrong_logic", "reason": "missing_two_pointer_swap"}

    if problem_name == "Fibonacci Recursion":
        has_base = any(k in code_lower for k in ["n <= 1", "n==0", "n == 0", "n == 1"])
        has_recur = "fib(" in code_lower and "n-1" in code_lower
        has_second = "n-2" in code_lower
        if has_base and has_recur and has_second:
            return {"passed": True, "failure_type": "", "reason": "pass"}
        if has_recur and not has_base:
            return {"passed": False, "failure_type": "wrong_logic", "reason": "missing_base_case"}
        return {"passed": False, "failure_type": "needs_test_validation", "reason": "incomplete_recursion"}

    if problem_name == "Valid Parentheses":
        has_stack = "stack" in code_lower
        has_push_pop = any(k in code_lower for k in ["push", "pop", "append", "remove"])
        has_validation = any(k in code_lower for k in ["return false", "return true", "isempty", "len(stack)"])
        if has_stack and has_push_pop and has_validation:
            return {"passed": True, "failure_type": "", "reason": "pass"}
        if has_stack and not has_push_pop:
            return {"passed": False, "failure_type": "wrong_logic", "reason": "stack_not_used_correctly"}
        return {"passed": False, "failure_type": "needs_test_validation", "reason": "parentheses_logic_unclear"}

    return {"passed": False, "failure_type": "needs_test_validation", "reason": "unsupported_evaluator"}
