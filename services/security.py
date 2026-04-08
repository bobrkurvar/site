import bcrypt

from core import conf
import hashlib

def normalize_input(string: str) -> bytes:
    combined = (string + conf.pepper).encode()
    return hashlib.sha256(combined).digest()[:72]

def get_hash(string: str) -> str:
    normalized = normalize_input(string)
    hashed = bcrypt.hashpw(normalized, bcrypt.gensalt())
    return hashed.decode()

def verify(string: str, hashed: str) -> bool:
    normalized = normalize_input(string)
    return bcrypt.checkpw(normalized, hashed.encode())

def compute_user_fingerprint(user_agent, client):
    combined = user_agent + str(client)
    return combined

# def get_hash(string: str) -> str:
#     salt = bcrypt.gensalt()
#     combined = (string + conf.pepper).encode()[:72]
#     hashed = bcrypt.hashpw(combined, salt)
#     return hashed.decode()
#
#
# def verify(password: str, hashed: str) -> bool:
#     combined = (password + conf.pepper).encode()
#     return bcrypt.checkpw(combined, hashed.encode())
