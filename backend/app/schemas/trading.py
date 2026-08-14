#نماذج Pydantic للتداول
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import uuid
from decimal import Decimal

# ===== Portfolio =====
class PortfolioBase(BaseModel):
    name: Optional[str] = "المحفظة الرئيسية"
    currency: Optional[str] = "USD"

class PortfolioCreate(PortfolioBase):
    user_id: uuid.UUID

class PortfolioResponse(PortfolioBase):
    id: uuid.UUID
    user_id: uuid.UUID
    virtual_balance: Decimal
    total_invested: Decimal
    total_profit_loss: Decimal
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ===== Position =====
class PositionResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    symbol: str
    asset_name: str
    asset_logo: Optional[str]
    quantity: Decimal
    average_price: Decimal
    current_price: Optional[Decimal]
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    market_value: Optional[Decimal]
    profit_percent: Optional[Decimal]

    class Config:
        from_attributes = True

# ===== Order =====
class OrderBase(BaseModel):
    asset_symbol: str
    side: str = Field(..., pattern="^(BUY|SELL)$")
    order_type: str = Field(..., pattern="^(MARKET|LIMIT|STOP_LOSS|TAKE_PROFIT)$")
    quantity: Decimal = Field(..., gt=0)
    price: Optional[Decimal] = Field(None, gt=0)
    stop_price: Optional[Decimal] = Field(None, gt=0)

    @field_validator('price')
    def validate_limit_price(cls, v, info):
        if info.data.get('order_type') == 'LIMIT' and v is None:
            raise ValueError('يجب تحديد السعر للأوامر المحددة (LIMIT)')
        return v

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    asset_id: uuid.UUID
    status: str
    filled_quantity: Decimal
    average_fill_price: Optional[Decimal]
    fee: Decimal
    fee_currency: str
    notes: Optional[str]
    executed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ===== Trade =====
class TradeResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    portfolio_id: uuid.UUID
    asset_id: uuid.UUID
    side: str
    quantity: Decimal
    price: Decimal
    fee: Decimal
    fee_currency: str
    executed_at: datetime

    class Config:
        from_attributes = True

# ===== Ledger =====
class LedgerResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    user_id: uuid.UUID
    type: str
    amount: Decimal
    currency: str
    reference_id: Optional[uuid.UUID]
    description: Optional[str]
    metadata: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True

# ===== Portfolio Summary =====
class PortfolioSummary(BaseModel):
    portfolio: PortfolioResponse
    total_balance: Decimal
    available_balance: Decimal
    invested: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    total_pnl: Decimal
    positions_count: int
    positions: List[PositionResponse]
    recent_orders: List[OrderResponse]
    recent_trades: List[TradeResponse]

    class Config:
        from_attributes = True