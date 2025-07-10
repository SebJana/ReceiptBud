from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import UserLogin, UserCreate
from app.auth.auth_handler import create_token
from app.auth.auth_bearer import JWTBearer
import bcrypt
import uuid
from datetime import datetime, timezone

router = APIRouter()

@router.post("/register")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user.username = user.username.strip()
    if not user.username:
        raise HTTPException(status_code=400, detail="Username can not be empty")
    
    if not valid_username_length(user.username):
        raise HTTPException(status_code=400, detail="Username doesn't meet length requirements")
    
    # Username can't contain any space
    space = " "
    if space in user.username:
        raise HTTPException(status_code=400, detail="Username can't contain space")

    # Dont allow special characters to not allow query injection
    if not valid_username_special_chars(user.username):
        raise HTTPException(status_code=400, detail="Username can't contain special characters")
    
    if not valid_username_restricted_names(user.username):
        raise HTTPException(status_code=400, detail="This username is protected and can't be used")
    
    if not available_username(user.username, db):
        raise HTTPException(status_code=400, detail="User already registered")
    
    user.password = user.password.strip()
    if not user.password:
        raise HTTPException(status_code=400, detail="Password can not be empty")
    
    if not valid_password(user.password):
        raise HTTPException(status_code=400, detail="Password doesn't meet security requirements")

    new_user = User(
        id = str(uuid.uuid4()), # Unique user id
        username=user.username,
        password_hash=hash_password(user.password),
        created_at=datetime.now(timezone.utc)
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="DB error")

    return {"message" : "User was created successfully"}

def available_username(username, db):
    same_username = db.query(User).filter(User.username == username).first()
    if same_username:
        return False
    return True

def valid_username_special_chars(username):
    special_chars = "!#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\""
    for char in username:
        if char in special_chars:
            return False
    return True

def valid_username_restricted_names(username):
    protected_names = ["admin", "root", "superuser", "api", "mongo", "system", "config", "local", "support", "help", "moderator", "mod", "staff", "test", "helper", "me", "login", "register", "staff"]

    if username.lower() in protected_names:
        return False
    return True

def valid_username_length(username):
    length = len(username)
    min_length = 3
    max_length = 30
    
    if length < min_length or length > max_length:
        return False
    return True

def valid_password(password):
    min_length = 8
    max_length = 30
    length = len(password)
    if length < min_length or length > max_length:
        return False

    # password can not contain space
    space = " "
    if space in password:
        return False
    
    # password contains at least 1 capital letter, 1 number, 1 special character
    special_character = False
    contains_digit = False
    contains_capital_letter = False
    special_chars = "!#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\""
    
    for char in password:
        if not special_character and char in special_chars:
            special_character = True
        if char.isdigit():
            contains_digit = True
        if char.isupper():
            contains_capital_letter = True
            
    if not special_character or not contains_digit or not contains_capital_letter:
        return False
    return True

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode()


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Check valid username again so that no query runs if username could potentially be harmful
    username = user.username

    if not valid_username_special_chars(username) or not valid_username_restricted_names(username):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    db_user = db.query(User).filter(User.username == username).first()

    if not db_user: # Check if user with that name exists
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    db_password_bytes = db_user.password_hash.encode("utf-8")
    password_bytes = user.password.encode("utf-8")

    if not bcrypt.checkpw(password_bytes, db_password_bytes): # Check if password is valid
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return create_token(db_user.id, db_user.username, user.remember_me)

@router.get("/me")
def return_logged_in_user(payload: dict = Depends(JWTBearer())):
    username = payload.get("username")
    token_type = payload.get("type")

    if token_type != "access":
        raise HTTPException(status_code=403, detail="Invalid token type for checking if logged in")
    return {"username" : username}

@router.post("/refresh_access_token")
def refresh_access_token(payload: dict = Depends(JWTBearer())):
    user_id = payload.get("sub")
    username = payload.get("username")
    token_type = payload.get("type")

    # Only let refresh tokens create new access tokens, so that no access token can infinitely refresh itself
    if token_type != "refresh":
        raise HTTPException(status_code=403, detail="Invalid token type for refresh of access token")
    # Just generate an access token and not a new refresh token, therefore set refresh_token to False
    return create_token(user_id, username, False) 
