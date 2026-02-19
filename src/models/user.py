from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    telegram_id: int
    name: str
    state: str = "new"


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: str
    company_id: str | None = None
    created_at: datetime
    updated_at: datetime
