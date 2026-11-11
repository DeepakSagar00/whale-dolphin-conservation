"""Authentication: PBKDF2 password hashing + JWT tokens."""
import hashlib
import hmac
import time

import jwt

SECRET = "dev-secret-change-in-production"
ALGO = "HS256"
TOKEN_TTL = 3600 * 12  # 12 hours


def hash_password(password: str, salt: bytes = b"mv1-salt") -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()


def verify_password(password: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), stored_hash)


def create_token(user_id: int, username: str, role: str) -> str:
    payload = {"sub": str(user_id), "username": username, "role": role,
               "exp": int(time.time()) + TOKEN_TTL}
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALGO])