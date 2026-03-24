from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class HysaLogSchema(BaseModel):
    id: Optional[UUID] = None
    log_date: date
    amount: Decimal
    log_type: str
    note: Optional[str] = ""

    class Config:
        from_attributes = True


class HysaSnapshotSchema(BaseModel):
    snapshot_date: date
    balance: Decimal

    class Config:
        from_attributes = True


class HysaAccountResponse(BaseModel):
    id: UUID
    ticker: Optional[str] = None
    name: Optional[str] = None
    current_balance: Decimal
    apy_rate: Decimal
    compounding: int
    frequency: str
    contribution_target: Decimal
    next_contribution_date: Optional[date] = None
    annual_deposit: Decimal
    sort_order: int
    logs: list[HysaLogSchema] = []
    snapshots: list[HysaSnapshotSchema] = []

    class Config:
        from_attributes = True


class HysaCreateRequest(BaseModel):
    ticker: Optional[str] = "NEW"
    name: Optional[str] = "New savings account"
    apy_rate: Decimal = Decimal("0.0450")
    compounding: int = 12
    current_balance: Decimal = Decimal("0")
    frequency: str = "monthly"
    contribution_target: Decimal = Decimal("0")
    next_contribution_date: Optional[date] = None
    annual_deposit: Decimal = Decimal("0")


class HysaUpdateRequest(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    current_balance: Optional[Decimal] = None
    apy_rate: Optional[Decimal] = None
    compounding: Optional[int] = None
    frequency: Optional[str] = None
    contribution_target: Optional[Decimal] = None
    next_contribution_date: Optional[date] = None
    annual_deposit: Optional[Decimal] = None


class HysaLogCreateRequest(BaseModel):
    date: date
    amount: Decimal
    type: str
    note: Optional[str] = ""