from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import UserLogin
from app.auth.auth_handler import create_token
import bcrypt

router = APIRouter()

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    pass

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
    return hashed_password