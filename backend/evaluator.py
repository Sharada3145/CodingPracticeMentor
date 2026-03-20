PROBLEM_HINTS = {
    "Two Sum": {"topic": "arrays", "hint": "Validate index boundaries and return early."},
    "Binary Search": {
        "topic": "search",
        "hint": "Double-check left/right movement and midpoint updates.",
    },
    "Reverse String": {
        "topic": "strings",
        "hint": "Verify two-pointer stop condition to avoid crossing errors.",
    },
    "Fibonacci Recursion": {
        "topic": "recursion",
        "hint": "Start with complete base cases before recursive calls.",
    },
    "Valid Parentheses": {
        "topic": "stacks",
        "hint": "Push opens and validate closes while checking stack emptiness.",
    },
}


def get_problem_topic(problem_name: str) -> str:
    if problem_name in PROBLEM_HINTS:
        return PROBLEM_HINTS[problem_name]["topic"]
    return "general"


def get_problem_hint(problem_name: str) -> str:
    if problem_name in PROBLEM_HINTS:
        return PROBLEM_HINTS[problem_name]["hint"]
    return "Practice adding edge-case tests before final submit."
