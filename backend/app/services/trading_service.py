#خدمة التداول والمحفظة
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import Optional, List, Dict, Any, Tuple
import uuid
from decimal import Decimal
from datetime import datetime, timezone
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..models.trading import (
    Portfolio, Position, Order, Trade, LedgerEntry,
    OrderSide, OrderType, OrderStatus, TradeType, LedgerType
)
from ..models.market import Asset, AssetType, AssetPrice
from ..schemas.trading import OrderCreate
from ..core.config import settings
from ..core.database import SessionLocal

logger = logging.getLogger(__name__)

class TradingService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_portfolio(self, user_id: uuid.UUID) -> Portfolio:
        """الحصول على محفظة المستخدم أو إنشاؤها"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            portfolio = Portfolio(
                user_id=user_id,
                virtual_balance=settings.DEFAULT_VIRTUAL_BALANCE,
                currency="USD"
            )
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)

            ledger = LedgerEntry(
                portfolio_id=portfolio.id,
                user_id=user_id,
                type=LedgerType.DEPOSIT,
                amount=settings.DEFAULT_VIRTUAL_BALANCE,
                currency="USD",
                description="الإيداع الأولي للتداول التجريبي"
            )
            self.db.add(ledger)
            self.db.commit()

        return portfolio

    def get_portfolio_summary(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """الحصول على ملخص المحفظة"""
        portfolio = self.get_or_create_portfolio(user_id)

        positions = self.db.query(Position).filter(
            Position.portfolio_id == portfolio.id,
            Position.quantity > 0
        ).all()

        positions_data = []
        total_unrealized_pnl = Decimal('0.00')
        total_invested = Decimal('0.00')

        for pos in positions:
            latest_price = self.db.query(AssetPrice).filter(
                AssetPrice.asset_id == pos.asset_id
            ).order_by(desc(AssetPrice.timestamp)).first()

            current_price = latest_price.price if latest_price else pos.average_price
            market_value = current_price * pos.quantity
            unrealized_pnl = market_value - (pos.average_price * pos.quantity)

            pos.current_price = current_price
            pos.unrealized_pnl = unrealized_pnl
            self.db.commit()

            asset = self.db.query(Asset).filter(Asset.id == pos.asset_id).first()

            positions_data.append({
                "id": pos.id,
                "asset_id": pos.asset_id,
                "symbol": asset.symbol if asset else "N/A",
                "asset_name": asset.name if asset else "N/A",
                "asset_logo": asset.logo_url if asset else None,
                "quantity": pos.quantity,
                "average_price": pos.average_price,
                "current_price": current_price,
                "unrealized_pnl": unrealized_pnl,
                "realized_pnl": pos.realized_pnl,
                "market_value": market_value,
                "profit_percent": (unrealized_pnl / (pos.average_price * pos.quantity)) * 100 if pos.average_price * pos.quantity > 0 else 0
            })

            total_unrealized_pnl += unrealized_pnl
            total_invested += pos.average_price * pos.quantity

        recent_orders = self.db.query(Order).filter(
            Order.portfolio_id == portfolio.id
        ).order_by(desc(Order.created_at)).limit(5).all()

        recent_trades = self.db.query(Trade).filter(
            Trade.portfolio_id == portfolio.id
        ).order_by(desc(Trade.executed_at)).limit(5).all()

        total_balance = portfolio.virtual_balance + total_invested + total_unrealized_pnl

        return {
            "portfolio": portfolio,
            "total_balance": total_balance,
            "available_balance": portfolio.virtual_balance,
            "invested": total_invested,
            "unrealized_pnl": total_unrealized_pnl,
            "realized_pnl": portfolio.total_profit_loss,
            "total_pnl": total_unrealized_pnl + portfolio.total_profit_loss,
            "positions_count": len(positions_data),
            "positions": positions_data,
            "recent_orders": recent_orders,
            "recent_trades": recent_trades
        }

    def update_position(self, portfolio_id: uuid.UUID, asset_id: uuid.UUID, quantity: Decimal, price: Decimal, side: str) -> Position:
        """تحديث المركز"""
        position = self.db.query(Position).filter(
            Position.portfolio_id == portfolio_id,
            Position.asset_id == asset_id
        ).first()

        if not position:
            position = Position(
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                quantity=0,
                average_price=0
            )
            self.db.add(position)

        if side == OrderSide.BUY:
            total_cost = position.average_price * position.quantity + price * quantity
            new_quantity = position.quantity + quantity
            position.average_price = total_cost / new_quantity if new_quantity > 0 else 0
            position.quantity = new_quantity
        else:
            if position.quantity < quantity:
                raise ValueError("الكمية المطلوبة للبيع أكبر من الكمية المتوفرة")

            avg_price = position.average_price
            realized_pnl = (price - avg_price) * quantity

            position.quantity = position.quantity - quantity
            position.realized_pnl += realized_pnl

            if position.quantity == 0:
                position.average_price = 0

            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if portfolio:
                portfolio.total_profit_loss += realized_pnl

        self.db.commit()
        self.db.refresh(position)
        return position

    def create_order(self, user_id: uuid.UUID, order_data: OrderCreate) -> Order:
        """إنشاء أمر شراء/بيع جديد"""
        portfolio = self.get_or_create_portfolio(user_id)

        asset = self.db.query(Asset).filter(Asset.symbol == order_data.asset_symbol).first()
        if not asset:
            raise ValueError(f"الأصل {order_data.asset_symbol} غير موجود")

        if asset.status != "ACTIVE":
            raise ValueError(f"الأصل {order_data.asset_symbol} غير نشط")

        latest_price = self.db.query(AssetPrice).filter(
            AssetPrice.asset_id == asset.id
        ).order_by(desc(AssetPrice.timestamp)).first()

        if not latest_price:
            raise ValueError(f"لا توجد بيانات سعرية للأصل {order_data.asset_symbol}")

        current_price = latest_price.price

        if order_data.quantity <= 0:
            raise ValueError("الكمية يجب أن تكون أكبر من صفر")

        if order_data.side == OrderSide.BUY:
            total_cost = order_data.quantity * (order_data.price if order_data.order_type == OrderType.LIMIT and order_data.price else current_price)
            if total_cost > portfolio.virtual_balance:
                raise ValueError(f"الرصيد غير كافٍ. المطلوب: ${total_cost:.2f}، المتاح: ${portfolio.virtual_balance:.2f}")

        if order_data.side == OrderSide.SELL:
            position = self.db.query(Position).filter(
                Position.portfolio_id == portfolio.id,
                Position.asset_id == asset.id
            ).first()

            if not position or position.quantity < order_data.quantity:
                raise ValueError(f"لا تملك كمية كافية من {order_data.asset_symbol} للبيع")

        order = Order(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            side=order_data.side,
            order_type=order_data.order_type,
            quantity=order_data.quantity,
            price=order_data.price if order_data.order_type == OrderType.LIMIT else None,
            stop_price=order_data.stop_price,
            status=OrderStatus.NEW,
            fee=0,
            fee_currency="USD"
        )

        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        if order_data.order_type == OrderType.MARKET:
            self.execute_order(order.id)

        return order

    def execute_order(self, order_id: uuid.UUID) -> Order:
        """تنفيذ أمر (تداول)"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("الأمر غير موجود")

        if order.status not in [OrderStatus.NEW, OrderStatus.PENDING]:
            raise ValueError(f"لا يمكن تنفيذ أمر بحالة {order.status}")

        latest_price = self.db.query(AssetPrice).filter(
            AssetPrice.asset_id == order.asset_id
        ).order_by(desc(AssetPrice.timestamp)).first()

        if not latest_price:
            raise ValueError("لا توجد بيانات سعرية")

        execution_price = latest_price.price

        # معالجة أوامر LIMIT
        if order.order_type == OrderType.LIMIT:
            if order.side == OrderSide.BUY and execution_price > order.price:
                order.status = OrderStatus.PENDING
                self.db.commit()
                logger.info(f"Order {order.id} set to PENDING (BUY limit {order.price} > market {execution_price})")
                return order
            elif order.side == OrderSide.SELL and execution_price < order.price:
                order.status = OrderStatus.PENDING
                self.db.commit()
                logger.info(f"Order {order.id} set to PENDING (SELL limit {order.price} < market {execution_price})")
                return order

        # تنفيذ الصفقة
        return self._execute_trade(order, execution_price)

    def _execute_trade(self, order: Order, execution_price: Decimal) -> Order:
        """تنفيذ الصفقة الفعلية"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.id == order.portfolio_id).first()

        fee = order.quantity * execution_price * Decimal(str(settings.TRADING_FEE_PERCENT))
        total_cost = order.quantity * execution_price + fee if order.side == OrderSide.BUY else order.quantity * execution_price - fee

        if order.side == OrderSide.BUY:
            if total_cost > portfolio.virtual_balance:
                raise ValueError(f"الرصيد غير كافٍ")
            portfolio.virtual_balance -= total_cost
        else:
            portfolio.virtual_balance += total_cost

        position = self.update_position(
            portfolio_id=order.portfolio_id,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price=execution_price,
            side=order.side
        )

        trade = Trade(
            order_id=order.id,
            portfolio_id=order.portfolio_id,
            asset_id=order.asset_id,
            side=order.side,
            quantity=order.quantity,
            price=execution_price,
            fee=fee,
            fee_currency="USD",
            executed_at=datetime.now(timezone.utc)
        )
        self.db.add(trade)

        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_fill_price = execution_price
        order.fee = fee
        order.executed_at = datetime.now(timezone.utc)

        ledger = LedgerEntry(
            portfolio_id=order.portfolio_id,
            user_id=portfolio.user_id,
            type=LedgerType.TRADE,
            amount=total_cost if order.side == OrderSide.BUY else -total_cost,
            currency="USD",
            reference_id=order.id,
            description=f"{'شراء' if order.side == OrderSide.BUY else 'بيع'} {order.quantity} من {order.asset.symbol}"
        )
        self.db.add(ledger)

        if fee > 0:
            fee_ledger = LedgerEntry(
                portfolio_id=order.portfolio_id,
                user_id=portfolio.user_id,
                type=LedgerType.FEE,
                amount=-fee,
                currency="USD",
                reference_id=order.id,
                description=f"رسوم تداول {order.asset.symbol}"
            )
            self.db.add(fee_ledger)

        self.db.commit()
        self.db.refresh(order)
        logger.info(f"Order {order.id} executed at {execution_price}")
        return order

    def cancel_order(self, order_id: uuid.UUID) -> Order:
        """إلغاء أمر معلق"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("الأمر غير موجود")

        if order.status not in [OrderStatus.NEW, OrderStatus.PENDING]:
            raise ValueError(f"لا يمكن إلغاء أمر بحالة {order.status}")

        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(order)
        logger.info(f"Order {order.id} cancelled")
        return order

    def get_ledger_entries(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[LedgerEntry]:
        portfolio = self.get_or_create_portfolio(user_id)
        return self.db.query(LedgerEntry).filter(
            LedgerEntry.portfolio_id == portfolio.id
        ).order_by(desc(LedgerEntry.created_at)).offset(offset).limit(limit).all()

    def get_orders(self, user_id: uuid.UUID, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Order]:
        portfolio = self.get_or_create_portfolio(user_id)
        query = self.db.query(Order).filter(Order.portfolio_id == portfolio.id)
        if status:
            query = query.filter(Order.status == status)
        return query.order_by(desc(Order.created_at)).offset(offset).limit(limit).all()

    def get_trades(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[Trade]:
        portfolio = self.get_or_create_portfolio(user_id)
        return self.db.query(Trade).filter(
            Trade.portfolio_id == portfolio.id
        ).order_by(desc(Trade.executed_at)).offset(offset).limit(limit).all()


# ===== Scheduler لفحص الأوامر المعلقة =====
def check_pending_orders():
    """فحص الأوامر المعلقة وتنفيذها عند تحقيق السعر"""
    db = SessionLocal()
    try:
        pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).all()
        for order in pending_orders:
            latest_price = db.query(AssetPrice).filter(
                AssetPrice.asset_id == order.asset_id
            ).order_by(desc(AssetPrice.timestamp)).first()
            if not latest_price:
                continue
            
            price = latest_price.price
            should_execute = False
            
            if order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and price <= order.price:
                    should_execute = True
                elif order.side == OrderSide.SELL and price >= order.price:
                    should_execute = True
            
            if should_execute:
                try:
                    trading_service = TradingService(db)
                    trading_service.execute_order(order.id)
                    logger.info(f"Executed pending order {order.id} at price {price}")
                except Exception as e:
                    logger.error(f"Failed to execute pending order {order.id}: {e}")
    except Exception as e:
        logger.error(f"Error in check_pending_orders: {e}")
    finally:
        db.close()

# بدء الجدولة
scheduler = BackgroundScheduler()
scheduler.add_job(check_pending_orders, IntervalTrigger(seconds=10))
scheduler.start()
logger.info("Pending orders scheduler started")