import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Init Engine (no connection yet)
engine = create_engine(DATABASE_URL, echo=True)

# Retry connections with sleep interval
MAX_RETRIES = 10
for i in range(MAX_RETRIES):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("DB connection established.")
        break
    except OperationalError:
        print(f"DB not ready, retrying {i+1}/{MAX_RETRIES} ...")
        time.sleep(10)
else:
    raise RuntimeError("Could not connect to the database after multiple retries.")

# ORM Setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
