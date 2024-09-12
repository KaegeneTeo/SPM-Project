from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    username: str
    email: str
    password: str
    password_hash: str | None = None

class LoginUser(BaseModel):
    username: str
    password: str