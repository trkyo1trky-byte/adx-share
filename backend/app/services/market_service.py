from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, or_, func
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime, timedelta, timezone
import httpx
import json

from ..models.market import Exchange, Sector, Asset, AssetPrice, AssetStatus, AssetType, ExchangeStatus
from ..schemas.market import (
    ExchangeCreate, SectorCreate, AssetCreate,
    MarketDataQuery, AssetHistoryQuery
)
from ..core.config import settings

class MarketService:
    def __init__(self, db: Session):
        self.db = db

    # ===== Exchanges =====
    def get_exchanges(self, active_only: bool = True) -> List[Exchange]:
        """الحصول على جميع البورصات"""
        query = self.db.query(Exchange)
        if active_only:
            query = query.filter(Exchange.status == ExchangeStatus.ACTIVE)
        return query.order_by(Exchange.code).all()

    def get_exchange_by_code(self, code: str) -> Optional[Exchange]:
        """الحصول على بورصة بواسطة الرمز"""
        return self.db.query(Exchange).filter(Exchange.code == code).first()

    def create_exchange(self, data: ExchangeCreate) -> Exchange:
        """إنشاء بورصة جديدة"""
        exchange = Exchange(**data.model_dump())
        self.db.add(exchange)
        self.db.commit()
        self.db.refresh(exchange)
        return exchange

    # ===== Sectors =====
    def get_sectors(self) -> List[Sector]:
        """الحصول على جميع القطاعات"""
        return self.db.query(Sector).order_by(Sector.name).all()

    def create_sector(self, data: SectorCreate) -> Sector:
        """إنشاء قطاع جديد"""
        sector = Sector(**data.model_dump())
        self.db.add(sector)
        self.db.commit()
        self.db.refresh(sector)
        return sector

    # ===== Assets =====
    def get_assets(self, query_params: MarketDataQuery) -> Dict[str, Any]:
        """الحصول على الأصول مع الفلاتر والترتيب"""
        query = self.db.query(Asset).filter(Asset.status == AssetStatus.ACTIVE)

        # تطبيق الفلاتر
        if query_params.symbol:
            query = query.filter(
                or_(
                    Asset.symbol.ilike(f"%{query_params.symbol}%"),
                    Asset.name.ilike(f"%{query_params.symbol}%"),
                    Asset.name_ar.ilike(f"%{query_params.symbol}%")
                )
            )

        if query_params.asset_type:
            query = query.filter(Asset.asset_type == query_params.asset_type)

        if query_params.exchange_code:
            query = query.join(Exchange).filter(Exchange.code == query_params.exchange_code)

        if query_params.sector:
            query = query.join(Sector).filter(Sector.name == query_params.sector)

        # الحصول على العدد الإجمالي
        total = query.count()

        # الترتيب
        sort_column = getattr(Asset, query_params.sort_by, Asset.market_cap)
        if query_params.sort_order == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        # التقسيم
        assets = query.offset(query_params.offset).limit(query_params.limit).all()

        return {
            "assets": assets,
            "total": total,
            "limit": query_params.limit,
            "offset": query_params.offset
        }

    def get_asset_by_symbol(self, symbol: str) -> Optional[Asset]:
        """الحصول على أصل بواسطة الرمز"""
        return self.db.query(Asset).filter(Asset.symbol == symbol).first()

    def get_asset_with_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """الحصول على أصل مع آخر سعر له"""
        asset = self.get_asset_by_symbol(symbol)
        if not asset:
            return None

        latest_price = self.db.query(AssetPrice).filter(
            AssetPrice.asset_id == asset.id
        ).order_by(desc(AssetPrice.timestamp)).first()

        return {
            "asset": asset,
            "price": latest_price
        }

    def create_asset(self, data: AssetCreate) -> Asset:
        """إنشاء أصل جديد"""
        asset = Asset(**data.model_dump())
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def get_asset_history(self, query: AssetHistoryQuery) -> List[AssetPrice]:
        """الحصول على البيانات التاريخية لأصل"""
        asset = self.get_asset_by_symbol(query.symbol)
        if not asset:
            return []

        # تحديد الفترة الزمنية
        now = datetime.now(timezone.utc)
        timeframe_map = {
            "1D": timedelta(days=1),
            "1W": timedelta(days=7),
            "1M": timedelta(days=30),
            "3M": timedelta(days=90),
            "6M": timedelta(days=180),
            "1Y": timedelta(days=365),
            "ALL": None
        }

        since = timeframe_map.get(query.timeframe)
        db_query = self.db.query(AssetPrice).filter(AssetPrice.asset_id == asset.id)

        if since:
            db_query = db_query.filter(AssetPrice.timestamp >= (now - since))

        return db_query.order_by(AssetPrice.timestamp).limit(query.limit).all()

    # ===== Market Data Fetch =====
    async def fetch_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """جلب بيانات السوق من مزود خارجي (محاكاة)"""
        # في الواقع، سيتم الاتصال بمزود بيانات مثل Alpha Vantage أو Yahoo Finance
        # ولكن في هذه المرحلة، نستخدم محاكاة للبيانات
        try:
            # محاكاة جلب البيانات
            import random
            base_price = random.uniform(10, 500)
            change = random.uniform(-5, 5)
            change_percent = (change / base_price) * 100

            return {
                "symbol": symbol,
                "price": round(base_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "high": round(base_price + random.uniform(0, 10), 2),
                "low": round(base_price - random.uniform(0, 10), 2),
                "volume": random.randint(100000, 10000000),
                "market_cap": round(base_price * random.randint(1000000, 1000000000), 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None

    # ===== Price Update =====
    def update_asset_price(self, asset_id: uuid.UUID, price_data: Dict[str, Any]) -> AssetPrice:
        """تحديث سعر الأصل"""
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError("Asset not found")

        # إنشاء سعر جديد
        new_price = AssetPrice(
            asset_id=asset_id,
            price=price_data.get("price", 0),
            open=price_data.get("open"),
            high=price_data.get("high"),
            low=price_data.get("low"),
            close=price_data.get("close"),
            change=price_data.get("change"),
            change_percent=price_data.get("change_percent"),
            volume=price_data.get("volume"),
            market_cap=price_data.get("market_cap"),
            high_24h=price_data.get("high_24h"),
            low_24h=price_data.get("low_24h"),
            timestamp=datetime.fromisoformat(price_data.get("timestamp")) if price_data.get("timestamp") else datetime.now(timezone.utc),
            source=price_data.get("source", "provider"),
            is_stale=price_data.get("is_stale", False)
        )

        self.db.add(new_price)
        self.db.commit()
        self.db.refresh(new_price)

        return new_price