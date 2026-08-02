from app.core.security import create_refresh_token, hash_token

def test_refresh_tokens_are_random_and_hashed():
    first, first_hash, _ = create_refresh_token(); second, second_hash, _ = create_refresh_token()
    assert first != second
    assert first_hash == hash_token(first)
    assert first_hash != second_hash
