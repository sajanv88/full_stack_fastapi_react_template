from passlib.hash import pbkdf2_sha256

import logging
logger = logging.getLogger(__name__)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.debug(f"Verifying password for user {plain_password} ... {hashed_password[:4]}***")
    result = pbkdf2_sha256.verify(plain_password, hashed_password)
    logger.debug(f"Password verification result: {result}")
    return result

def get_password_hash(password: str) -> str:
    logger.debug(f"Hashing password for user")
    return pbkdf2_sha256.hash(password)