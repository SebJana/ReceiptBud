from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth.auth_bearer import JWTBearer

router = APIRouter()

@router.get("/", dependencies=[Depends(JWTBearer())])
def get_all_receipts(db: Session = Depends(get_db)):
    pass

@router.post("/", dependencies=[Depends(JWTBearer())])
def create_receipt(db: Session = Depends(get_db)):
    pass