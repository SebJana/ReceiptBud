from fastapi import FastAPI
from app.db import Base, engine
from app.routes import auth, receipts

# Create all tables from SQLAlchemy models (if not exist)
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ReceiptBud API",
    version="1.0.0"
)

# Mount routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(receipts.router, prefix="/api/receipts", tags=["Receipts"])