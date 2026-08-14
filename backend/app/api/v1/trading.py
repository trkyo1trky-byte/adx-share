#(نقاط نهاية التداول
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Any
import uuid

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...services.trading_service import TradingService
from ...schemas.trading import (
    OrderCreate, OrderResponse, TradeResponse,
    PortfolioResponse, PortfolioSummary,
    LedgerResponse, PositionResponse
)

router = APIRouter(prefix="/trading", tags=["Trading"])

# ===== Portfolio =====
@router.get("/portfolio", response_model=PortfolioSummary)
async def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """الحصول على ملخص المحفظة الكامل"""
    service = TradingService(db)
    return service.get_portfolio_summary(current_user.id)

@router.get("/portfolio/positions", response_model=List[PositionResponse])
async def get_positions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """الحصول على المراكز المفتوحة"""
    service = TradingService(db)
    summary = service.get_portfolio_summary(current_user.id)
    return summary["positions"]

# ===== Orders =====
@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """إنشاء أمر شراء/بيع جديد"""
    try:
        service = TradingService(db)
        order = service.create_order(current_user.id, order_data)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """الحصول على طلبات المستخدم"""
    service = TradingService(db)
    return service.get_orders(current_user.id, status, limit, offset)

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """الحصول على تفاصيل أمر معين"""
    service = TradingService(db)
    order = service.db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="الأمر غير موجود")
    return order

@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """إلغاء أمر معلق"""
    try:
        service = TradingService(db)
        order = service.cancel_order(order_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# ===== Trades =====
@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """الحصول على سجل الصفقات"""
    service = TradingService(db)
    return service.get_trades(current_user.id, limit, offset)

# ===== Ledger =====
@router.get("/ledger", response_model=List[LedgerResponse])
async def get_ledger(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """الحصول على سجل دفتر الأستاذ"""
    service = TradingService(db)
    return service.get_ledger_entries(current_user.id, limit, offset)