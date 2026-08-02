from uuid import uuid4
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password

def test_password_hashing():
    encoded = hash_password("CorrectHorseBatteryStaple")
    assert encoded != "CorrectHorseBatteryStaple"
    assert verify_password("CorrectHorseBatteryStaple", encoded)
    assert not verify_password("wrong", encoded)

def test_access_token_roundtrip():
    user_id = uuid4(); token = create_access_token(user_id, "user")
    assert decode_access_token(token)["sub"] == str(user_id)
