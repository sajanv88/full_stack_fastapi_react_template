from passlib.hash import pbkdf2_sha256

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pbkdf2_sha256.hash(password)