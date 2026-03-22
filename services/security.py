import bcrypt

from core import conf


def get_hash(string: str) -> str:
    salt = bcrypt.gensalt()
    combined = (string + conf.pepper).encode()[:72]
    hashed = bcrypt.hashpw(combined, salt)
    return hashed.decode()


def verify(password: str, hashed: str) -> bool:
    combined = (password + conf.pepper).encode()
    return bcrypt.checkpw(combined, hashed.encode())
