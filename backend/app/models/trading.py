#نماذج التداول والمحفظة
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, ForeignKey, Numeric, Enum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from decimal import Decimal
from ..core.database import Base

# ===== Enums =====
class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"

class OrderStatus(str, enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class TradeType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class LedgerType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRADE = "TRADE"
    FEE = "FEE"
    REFUND = "REFUND"
    BONUS = "BONUS"
    ADJUSTMENT = "ADJUSTMENT"

# ===== Portfolio =====
class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    name = Column(String(100), default="المحفظة الرئيسية")
    currency = Column(String(10), default="USD")
    virtual_balance = Column(Numeric(20, 2), default=10000.00)
    total_invested = Column(Numeric(20, 2), default=0.00)
    total_profit_loss = Column(Numeric(20, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="portfolio")
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="portfolio", cascade="all, delete-orphan")
    ledger_entries = relationship("LedgerEntry", back_populates="portfolio", cascade="all, delete-orphan")

# ===== Position =====
class Position(Base):
    __tablename__ = "positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    quantity = Column(Numeric(20, 6), nullable=False, default=0)
    average_price = Column(Numeric(20, 6), nullable=False, default=0)
    current_price = Column(Numeric(20, 6), nullable=True)
    unrealized_pnl = Column(Numeric(20, 2), default=0.00)
    realized_pnl = Column(Numeric(20, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    portfolio = relationship("Portfolio", back_populates="positions")
    asset = relationship("Asset")

# ===== Order =====
class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    quantity = Column(Numeric(20, 6), nullable=False)
    price = Column(Numeric(20, 6), nullable=True)  # للسوقي: سعر التنفيذ، للحدي: السعر المحدد
    stop_price = Column(Numeric(20, 6), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.NEW)
    filled_quantity = Column(Numeric(20, 6), default=0)
    average_fill_price = Column(Numeric(20, 6), nullable=True)
    fee = Column(Numeric(20, 6), default=0)
    fee_currency = Column(String(10), default="USD")
    notes = Column(Text, nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    portfolio = relationship("Portfolio", back_populates="orders")
    asset = relationship("Asset")
    trades = relationship("Trade", back_populates="order", cascade="all, delete-orphan")

# ===== Trade =====
class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    side = Column(Enum(TradeType), nullable=False)
    quantity = Column(Numeric(20, 6), nullable=False)
    price = Column(Numeric(20, 6), nullable=False)
    fee = Column(Numeric(20, 6), default=0)
    fee_currency = Column(String(10), default="USD")
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="trades")
    portfolio = relationship("Portfolio")
    asset = relationship("Asset")

# ===== Ledger =====
class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(LedgerType), nullable=False)
    amount = Column(Numeric(20, 2), nullable=False)
    currency = Column(String(10), default="USD")
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # مرجع للـ Order أو Trade
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    portfolio = relationship("Portfolio", back_populates="ledger_entries")
    user = relationship("User")