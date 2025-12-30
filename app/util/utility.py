import hashlib

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    sha256_hashed = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(sha256_hashed)