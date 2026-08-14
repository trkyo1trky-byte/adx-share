from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Any
import uuid

from ...core.database import get_db
from ...core.dependencies import get_current_user, require_permission
from ...models.user import User
from ...services.market_service import MarketService
from ...schemas.market import (
    ExchangeResponse, ExchangeCreate,
    SectorResponse, SectorCreate,
    AssetResponse, AssetCreate,
    AssetPriceResponse,
    MarketSnapshotResponse,
    MarketDataQuery,
    AssetHistoryQuery
)

router = APIRouter(prefix="/markets", tags=["Markets"])

# ===== Exchanges =====
@router.get("/exchanges", response_model=List[ExchangeResponse])
async def get_exchanges(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """الحصول على جميع البورصات"""
    service = MarketService(db)
    return service.get_exchanges(active_only)

@router.get("/exchanges/{code}", response_model=ExchangeResponse)
async def get_exchange_by_code(
    code: str,
    db: Session = Depends(get_db)
):
    """الحصول على بورصة بواسطة الرمز"""
    service = MarketService(db)
    exchange = service.get_exchange_by_code(code)
    if not exchange:
        raise HTTPException(status_code=404, detail="البورصة غير موجودة")
    return exchange

@router.post("/exchanges", response_model=ExchangeResponse)
async def create_exchange(
    data: ExchangeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("market.manage"))
):
    """إنشاء بورصة جديدة (يتطلب صلاحية Admin)"""
    service = MarketService(db)
    return service.create_exchange(data)

# ===== Sectors =====
@router.get("/sectors", response_model=List[SectorResponse])
async def get_sectors(db: Session = Depends(get_db)):
    """الحصول على جميع القطاعات"""
    service = MarketService(db)
    return service.get_sectors()

@router.post("/sectors", response_model=SectorResponse)
async def create_sector(
    data: SectorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("market.manage"))
):
    """إنشاء قطاع جديد (يتطلب صلاحية Admin)"""
    service = MarketService(db)
    return service.create_sector(data)

# ===== Assets =====
@router.get("/assets", response_model=dict)
async def get_assets(
    symbol: Optional[str] = None,
    asset_type: Optional[str] = None,
    exchange_code: Optional[str] = None,
    sector: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sort_by: str = "market_cap",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    """الحصول على الأصول مع الفلاتر والترتيب"""
    query_params = MarketDataQuery(
        symbol=symbol,
        asset_type=asset_type,
        exchange_code=exchange_code,
        sector=sector,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    service = MarketService(db)
    return service.get_assets(query_params)

@router.get("/assets/{symbol}", response_model=dict)
async def get_asset_by_symbol(
    symbol: str,
    db: Session = Depends(get_db)
):
    """الحصول على تفاصيل أصل مع آخر سعر"""
    service = MarketService(db)
    result = service.get_asset_with_price(symbol)
    if not result:
        raise HTTPException(status_code=404, detail="الأصل غير موجود")
    return result

@router.post("/assets", response_model=AssetResponse)
async def create_asset(
    data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("market.manage"))
):
    """إنشاء أصل جديد (يتطلب صلاحية Admin)"""
    service = MarketService(db)
    return service.create_asset(data)

@router.get("/assets/{symbol}/history", response_model=List[AssetPriceResponse])
async def get_asset_history(
    symbol: str,
    timeframe: str = "1M",
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """الحصول على البيانات التاريخية لأصل"""
    query = AssetHistoryQuery(symbol=symbol, timeframe=timeframe, limit=limit)
    service = MarketService(db)
    history = service.get_asset_history(query)
    if not history:
        raise HTTPException(status_code=404, detail="الأصل غير موجود")
    return history

# ===== Market Snapshot =====
@router.get("/snapshots", response_model=List[MarketSnapshotResponse])
async def get_market_snapshots(
    exchange_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """الحصول على لقطات السوق"""
    # محاكاة: سيتم تنفيذها بالكامل في المرحلة القادمة
    return []