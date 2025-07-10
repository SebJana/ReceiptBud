from fastapi import HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
import os
import time

TOKEN_KEY = os.getenv("TOKEN_SECRET")
ALGORITHM = "HS256"

ACCESS_TOKEN_DURATION = 30 * 60 # 30 Mins
REFRESH_TOKEN_DURATION = 30 * 24 * 60 * 60 # 30 Days

def create_token(user_id, username, refresh_token):
    access_token_payload = create_token_payload(user_id, username, "access")
    access_token = jwt.encode(access_token_payload, TOKEN_KEY, algorithm=ALGORITHM)

    token_json = {
        "access_token": access_token,
    }

    # Create a refresh token if user requested one
    if refresh_token:
        refresh_token_payload = create_token_payload(user_id, username, "refresh")
        refresh_token = jwt.encode(refresh_token_payload, TOKEN_KEY, algorithm=ALGORITHM)
        token_json["refresh_token"] = refresh_token
    
    token_json["token_type"] = "bearer" # Add O2Auth2 Standard field

    return token_json

def create_token_payload(user_id, username, token_type):
    now = int(time.time()) # Make timestamp a round number

    # Determine how long the token will be valid for
    duration_till_expires = 0
    if token_type == "refresh":
        duration_till_expires = REFRESH_TOKEN_DURATION
    else:
        duration_till_expires = ACCESS_TOKEN_DURATION

    return {
        "sub": user_id,
        "username":  username,
        "type": token_type, # Needed to check token type for different usages
        "iat": now, # Issued at timestamp
        "exp": now + duration_till_expires # Expires at timestamp
    }

def verify_token(token: str):
    try:
        payload = jwt.decode(token, TOKEN_KEY, algorithms=ALGORITHM)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="This token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="This token is invalid")