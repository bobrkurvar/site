import hashlib
from uuid import uuid4

import bcrypt

from core import conf


def normalize_input(string: str) -> bytes:
    combined = (string + conf.pepper).encode()
    return hashlib.sha256(combined).hexdigest().encode()


def get_hash(string: str) -> str:
    normalized = normalize_input(string)
    hashed = bcrypt.hashpw(normalized, bcrypt.gensalt())
    return hashed.decode()


def verify(string: str, hashed: str) -> bool:
    normalized = normalize_input(string)
    return bcrypt.checkpw(normalized, hashed.encode())


def create_token_family_id() -> str:
    return uuid4().hex


def create_token_jti() -> str:
    return uuid4().hex


def calculate_file_hash(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()
