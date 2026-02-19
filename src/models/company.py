from pydantic import BaseModel
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    burn_rate: float = 0.0
    cash: float = 0.0


class CompanyCreate(CompanyBase):
    pass


class Company(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime
