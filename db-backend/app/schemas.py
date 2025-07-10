from pydantic import BaseModel

# Used for login input
class UserLogin(BaseModel):
    username: str
    password: str
    remember_me: bool

# Used when creating a user (e.g., via register)
class UserCreate(BaseModel):
    username: str
    password: str