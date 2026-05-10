from passlib.context import CryptContext
from app.extension import redis_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def increment_login_attempts(email):
    if not redis_client.get(f"attempts_passwd:{email}"):
        redis_client.setex(f"attempts_passwd:{email}", 3*3600, 1)
    else:
        redis_client.incr(f"attempts_passwd:{email}")
    return True