from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, Enum, ForeignKey, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from ..core.database import Base

class ExchangeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"
    CLOSED = "CLOSED"

class AssetStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    DELISTED = "DELISTED"

class AssetType(str, enum.Enum):
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    COMMODITY = "COMMODITY"
    FOREX = "FOREX"
    INDEX = "INDEX"
    ETF = "ETF"

class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=True)
    name_en = Column(String(100), nullable=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), default="Asia/Riyadh")
    currency = Column(String(10), default="USD")
    status = Column(Enum(ExchangeStatus), default=ExchangeStatus.ACTIVE)
    logo_url = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assets = relationship("Asset", back_populates="exchange", cascade="all, delete-orphan")
    market_snapshots = relationship("MarketSnapshot", back_populates="exchange", cascade="all, delete-orphan")

class Sector(Base):
    __tablename__ = "sectors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=True)
    name_en = Column(String(100), nullable=True)
    code = Column(String(20), unique=True, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sectors.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assets = relationship("Asset", back_populates="sector")
    children = relationship("Sector", backref="parent", remote_side=[id])

class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    name_en = Column(String(255), nullable=True)
    asset_type = Column(Enum(AssetType), nullable=False)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=True)
    sector_id = Column(UUID(as_uuid=True), ForeignKey("sectors.id"), nullable=True)
    isin = Column(String(20), nullable=True)
    currency = Column(String(10), default="USD")
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    logo_url = Column(String(500), nullable=True)
    description = Column(String(1000), nullable=True)
    description_ar = Column(String(1000), nullable=True)
    website = Column(String(500), nullable=True)
    ipo_date = Column(DateTime(timezone=True), nullable=True)
    shares_outstanding = Column(Numeric(20, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    exchange = relationship("Exchange", back_populates="assets")
    sector = relationship("Sector", back_populates="assets")
    prices = relationship("AssetPrice", back_populates="asset", cascade="all, delete-orphan")
    snapshots = relationship("MarketSnapshot", back_populates="asset", cascade="all, delete-orphan")
    
    # ===== الإضافة الجديدة =====
    crypto_detail = relationship("CryptoDetail", back_populates="asset", uselist=False, cascade="all, delete-orphan")

class AssetPrice(Base):
    __tablename__ = "asset_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    price = Column(Numeric(20, 6), nullable=False)
    open = Column(Numeric(20, 6), nullable=True)
    high = Column(Numeric(20, 6), nullable=True)
    low = Column(Numeric(20, 6), nullable=True)
    close = Column(Numeric(20, 6), nullable=True)
    change = Column(Numeric(20, 6), nullable=True)
    change_percent = Column(Numeric(10, 4), nullable=True)
    volume = Column(Numeric(20, 2), nullable=True)
    market_cap = Column(Numeric(20, 2), nullable=True)
    high_24h = Column(Numeric(20, 6), nullable=True)
    low_24h = Column(Numeric(20, 6), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(50), default="provider")
    is_stale = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    asset = relationship("Asset", back_populates="prices")

class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)
    index_name = Column(String(100), nullable=True)
    index_value = Column(Numeric(20, 6), nullable=True)
    change = Column(Numeric(20, 6), nullable=True)
    change_percent = Column(Numeric(10, 4), nullable=True)
    high = Column(Numeric(20, 6), nullable=True)
    low = Column(Numeric(20, 6), nullable=True)
    volume = Column(Numeric(20, 2), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(50), default="provider")

    exchange = relationship("Exchange", back_populates="market_snapshots")
    asset = relationship("Asset", back_populates="snapshots")