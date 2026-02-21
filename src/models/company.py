from pydantic import BaseModel
from datetime import datetime


class Company(BaseModel):
    id: str
    name: str
    cnpj: str | None = None
    email: str | None = None
    fixed_cost_avg: float = 0
    variable_cost_percent: float = 30
    cash_minimum: float = 5000
    alert_days_threshold: int = 10
    status: str = "trial"
    plan: str = "early_adopter"
    chat_id: int | None = None
    last_report_sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CompanyCreate(BaseModel):
    name: str
    status: str = "trial"
    plan: str = "early_adopter"
    fixed_cost_avg: float = 0
    variable_cost_percent: float = 30
    cash_minimum: float = 5000
    chat_id: int | None = None
