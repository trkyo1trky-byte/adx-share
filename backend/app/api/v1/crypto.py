#نقاط نهاية العملات الرقمية
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Any
import asyncio

from ...core.database import get_db
from ...core.dependencies import get_current_user, require_permission
from ...models.user import User
from ...services.crypto_service import CryptoService
from ...schemas.market import AssetResponse, AssetPriceResponse

router = APIRouter(prefix="/crypto", tags=["Crypto"])

@router.get("/markets")
async def get_crypto_markets(
    vs_currency: str = "usd",
    per_page: int = Query(100, ge=1, le=500),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    """جلب العملات الرقمية مباشرة من CoinGecko (بدون حفظ)"""
    service = CryptoService(db)
    data = await service.fetch_crypto_markets(vs_currency, per_page, page)
    return data

@router.get("/list")
async def get_crypto_list(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """الحصول على قائمة العملات الرقمية المخزنة محلياً"""
    service = CryptoService(db)
    return service.get_crypto_list(limit, offset)

@router.get("/{symbol}")
async def get_crypto_by_symbol(
    symbol: str,
    db: Session = Depends(get_db)
):
    """الحصول على تفاصيل عملة رقمية معينة"""
    service = CryptoService(db)
    result = service.get_crypto_by_symbol(symbol)
    if not result:
        raise HTTPException(status_code=404, detail="العملة غير موجودة")
    return result

@router.post("/sync")
async def sync_crypto_markets(
    per_page: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("market.manage"))
):
    """مزامنة العملات الرقمية من CoinGecko (يتطلب صلاحية Admin)"""
    service = CryptoService(db)
    count = await service.sync_crypto_markets(per_page)
    return {"message": f"تمت مزامنة {count} عملة رقمية بنجاح"}

@router.get("/{symbol}/history")
async def get_crypto_history(
    symbol: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """الحصول على البيانات التاريخية للعملة الرقمية"""
    # البحث عن العملة في قاعدة البيانات للحصول على coin_id
    service = CryptoService(db)
    result = service.get_crypto_by_symbol(symbol)
    if not result:
        raise HTTPException(status_code=404, detail="العملة غير موجودة")

    # محاولة جلب التاريخ من CoinGecko
    coin_id = result["asset"].symbol.lower()
    history = await service.fetch_crypto_history(coin_id, days)
    if history is None:
        raise HTTPException(status_code=404, detail="لا توجد بيانات تاريخية")
    return history