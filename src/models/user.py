from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: str
    company_id: str
    chat_id: int
    telegram_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    state: str = "new"
    current_action: str | None = None
    onboarding_step: int = 0
    last_interaction_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    chat_id: int
    telegram_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    state: str = "new"
    onboarding_step: int = 0
    company_id: str
