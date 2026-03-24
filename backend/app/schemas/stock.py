from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class StockLotSchema(BaseModel):
    id: Optional[UUID] = None
    purchase_date: Optional[date] = None
    shares: Decimal
    price_per_share: Decimal
    amount_spent: Decimal

    class Config:
        from_attributes = True


class StockPriceSchema(BaseModel):
    price_date: date
    price: Decimal

    class Config:
        from_attributes = True


class StockHoldingResponse(BaseModel):
    id: UUID
    ticker: str
    name: Optional[str] = None
    account_type: str
    exchange: Optional[str] = None
    quote_type: Optional[str] = None
    lots: list[StockLotSchema] = []
    price_history: list[StockPriceSchema] = []
    # Computed fields the frontend expects
    shares: Decimal = Decimal("0")
    buy_price: Decimal = Decimal("0")
    total_cost: Decimal = Decimal("0")

    class Config:
        from_attributes = True


class StockCreateRequest(BaseModel):
    ticker: str
    name: Optional[str] = None
    account_type: str = "Roth IRA"
    exchange: Optional[str] = None
    quote_type: Optional[str] = None
    # First lot
    purchase_date: Optional[date] = None
    shares: Decimal
    price_per_share: Decimal
    amount_spent: Decimal


class StockUpdateRequest(BaseModel):
    name: Optional[str] = None
    account_type: Optional[str] = None


class LotCreateRequest(BaseModel):
    purchase_date: Optional[date] = None
    shares: Decimal
    price_per_share: Decimal
    amount_spent: Decimal


class LotUpdateRequest(BaseModel):
    purchase_date: Optional[date] = None
    shares: Optional[Decimal] = None
    price_per_share: Optional[Decimal] = None
    amount_spent: Optional[Decimal] = None


class PriceCreateRequest(BaseModel):
    date: date
    price: Decimal


class SnapshotRequest(BaseModel):
    date: date
    value: Decimal