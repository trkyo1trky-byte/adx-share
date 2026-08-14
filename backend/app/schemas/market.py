from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import uuid
from decimal import Decimal

# ===== Exchange Schemas =====
class ExchangeBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    name_en: Optional[str] = None
    code: str = Field(..., min_length=2, max_length=20)
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = "Asia/Riyadh"
    currency: Optional[str] = "USD"
    logo_url: Optional[str] = None
    website: Optional[str] = None

class ExchangeCreate(ExchangeBase):
    pass

class ExchangeResponse(ExchangeBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ===== Sector Schemas =====
class SectorBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    name_en: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None

class SectorCreate(SectorBase):
    pass

class SectorResponse(SectorBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ===== Asset Schemas =====
class AssetBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=50)
    name: str
    name_ar: Optional[str] = None
    name_en: Optional[str] = None
    asset_type: str
    exchange_id: Optional[uuid.UUID] = None
    sector_id: Optional[uuid.UUID] = None
    isin: Optional[str] = None
    currency: Optional[str] = "USD"
    logo_url: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    website: Optional[str] = None
    ipo_date: Optional[datetime] = None
    shares_outstanding: Optional[Decimal] = None

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    exchange: Optional[ExchangeResponse] = None
    sector: Optional[SectorResponse] = None

    class Config:
        from_attributes = True

# ===== Asset Price Schemas =====
class AssetPriceResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    price: Decimal
    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    close: Optional[Decimal] = None
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    high_24h: Optional[Decimal] = None
    low_24h: Optional[Decimal] = None
    timestamp: datetime
    source: Optional[str] = None
    is_stale: bool = False

    class Config:
        from_attributes = True

# ===== Market Snapshot Schemas =====
class MarketSnapshotResponse(BaseModel):
    id: uuid.UUID
    exchange_id: Optional[uuid.UUID] = None
    asset_id: Optional[uuid.UUID] = None
    index_name: Optional[str] = None
    index_value: Optional[Decimal] = None
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# ===== Market Data Query =====
class MarketDataQuery(BaseModel):
    symbol: Optional[str] = None
    asset_type: Optional[str] = None
    exchange_code: Optional[str] = None
    sector: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_change: Optional[Decimal] = None
    max_change: Optional[Decimal] = None
    limit: int = Field(100, ge=1, le=500)
    offset: int = Field(0, ge=0)
    sort_by: Optional[str] = "market_cap"
    sort_order: Optional[str] = "desc"

class AssetHistoryQuery(BaseModel):
    symbol: str
    timeframe: str = Field(..., pattern="^(1D|1W|1M|3M|6M|1Y|ALL)$")
    limit: int = Field(100, ge=1, le=1000)