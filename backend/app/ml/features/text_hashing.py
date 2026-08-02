import hashlib
import re

TOKEN_PATTERN = re.compile(r"[\w-]+", re.UNICODE)


def token_ids(text: str, *, vocab_size: int, max_length: int) -> list[int]:
    """Map text to stable hashed token IDs without an external tokenizer download."""
    ids: list[int] = []
    for token in TOKEN_PATTERN.findall(text.lower())[:max_length]:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        ids.append(1 + int.from_bytes(digest, "big") % (vocab_size - 1))
    return ids or [1]
