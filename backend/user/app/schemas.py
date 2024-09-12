from pydantic import BaseModel
from datetime import datetime
from typing import List


class User(BaseModel):
    user_id: int | None = None
    username: str
    email: str
    password: str | None = None
    password_hash: str | None = None
    telegram_id : str | None = None
    telegram_tag: str | None = None
    image: str | None = None

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    password_hash: str
    telegram_id : str | None = None
    telegram_tag: str | None = None
    image: str | None = None

class UserIDs(BaseModel):
    user_ids: List[int]