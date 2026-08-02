import re

INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"ignore (all|any|the) previous instructions",
        r"reveal (the )?(system prompt|secret|api key)",
        r"you are now",
        r"developer message",
        r"execute (this )?(code|command)",
    )
]


def contains_prompt_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)


def sanitize_retrieved_text(text: str) -> str:
    """Mark suspicious instructions as untrusted data without deleting evidence."""
    if not contains_prompt_injection(text):
        return text
    return "[UNTRUSTED-INSTRUCTION-LIKE-CONTENT]\n" + text
