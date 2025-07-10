from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("TOKEN_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_token(user_id: int) -> str:
    pass

def verify_token(token: str) -> dict | None:
    pass