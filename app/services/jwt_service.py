from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = 'HS256'

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode['exp'] = datetime.utcnow() + timedelta(minutes=60)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")