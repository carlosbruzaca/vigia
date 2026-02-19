from pydantic import BaseModel
from datetime import datetime


class EntryBase(BaseModel):
    company_id: str
    entry_type: str
    amount: float
    description: str | None = None


class EntryCreate(EntryBase):
    pass


class Entry(EntryBase):
    id: str
    user_id: str
    created_at: datetime
