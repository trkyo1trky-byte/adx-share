#خدمة العملات الرقمية
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import asyncio

from ..models.market import Asset, AssetType, AssetStatus, AssetPrice
from ..models.crypto import CryptoDetail
from ..schemas.market import AssetCreate
from ..core.config import settings

class CryptoSettings:
    COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
    COINGECKO_MARKETS = f"{COINGECKO_API_URL}/coins/markets"
    COINGECKO_COIN = f"{COINGECKO_API_URL}/coins/{{id}}"
    COINGECKO_HISTORY = f"{COINGECKO_API_URL}/coins/{{id}}/market_chart"
    CACHE_TTL = 60  # ثانية

class CryptoService:
    def __init__(self, db: Session):
        self.db = db

    # ===== جلب البيانات من CoinGecko =====
    async def fetch_crypto_markets(self, vs_currency: str = "usd", per_page: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """جلب قائمة العملات الرقمية من CoinGecko"""
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
            "price_change_percentage": "1h,24h,7d,14d,30d,60d,200d,1y"
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(CryptoSettings.COINGECKO_MARKETS, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching crypto markets: {response.status_code} - {response.text}")
                return []

    async def fetch_crypto_detail(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """جلب تفاصيل عملة رقمية معينة"""
        url = CryptoSettings.COINGECKO_COIN.format(id=coin_id)
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false"
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching crypto detail for {coin_id}: {response.status_code}")
                return None

    async def fetch_crypto_history(self, coin_id: str, days: int = 30) -> Optional[List[Dict[str, Any]]]:
        """جلب البيانات التاريخية للعملة"""
        url = CryptoSettings.COINGECKO_HISTORY.format(id=coin_id)
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "daily" if days > 90 else "hourly"
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                prices = data.get("prices", [])
                return [{"timestamp": p[0], "price": p[1]} for p in prices]
            else:
                print(f"Error fetching crypto history for {coin_id}: {response.status_code}")
                return None

    # ===== حفظ البيانات في قاعدة البيانات =====
    def save_crypto_asset(self, crypto_data: Dict[str, Any]) -> Asset:
        """حفظ أو تحديث بيانات عملة رقمية في قاعدة البيانات"""
        symbol = crypto_data.get("symbol", "").upper()
        name = crypto_data.get("name", symbol)
        coin_id = crypto_data.get("id", symbol.lower())

        # البحث عن الأصل الموجود
        existing_asset = self.db.query(Asset).filter(Asset.symbol == symbol).first()

        if existing_asset:
            asset = existing_asset
            # تحديث البيانات الأساسية
            asset.name = name
            asset.name_en = name
            asset.name_ar = name  # يمكن تحسينه لاحقاً
            asset.logo_url = crypto_data.get("image", "")
            asset.updated_at = datetime.now(timezone.utc)
            self.db.commit()
        else:
            # إنشاء أصل جديد
            asset = Asset(
                symbol=symbol,
                name=name,
                name_en=name,
                name_ar=name,
                asset_type=AssetType.CRYPTO,
                status=AssetStatus.ACTIVE,
                logo_url=crypto_data.get("image", ""),
                currency="USD",
                description=crypto_data.get("description", {}).get("en", "")
            )
            self.db.add(asset)
            self.db.commit()
            self.db.refresh(asset)

        # حفظ أو تحديث السعر
        current_price = crypto_data.get("current_price", 0)
        if current_price:
            price_record = AssetPrice(
                asset_id=asset.id,
                price=current_price,
                open=crypto_data.get("price_change_24h", 0) + current_price if crypto_data.get("price_change_24h") else None,
                high=crypto_data.get("high_24h"),
                low=crypto_data.get("low_24h"),
                change=crypto_data.get("price_change_24h"),
                change_percent=crypto_data.get("price_change_percentage_24h"),
                volume=crypto_data.get("total_volume"),
                market_cap=crypto_data.get("market_cap"),
                high_24h=crypto_data.get("high_24h"),
                low_24h=crypto_data.get("low_24h"),
                timestamp=datetime.now(timezone.utc),
                source="coingecko",
                is_stale=False
            )
            self.db.add(price_record)

        # حفظ أو تحديث التفاصيل الإضافية
        crypto_detail = self.db.query(CryptoDetail).filter(CryptoDetail.asset_id == asset.id).first()
        if not crypto_detail:
            crypto_detail = CryptoDetail(asset_id=asset.id)
            self.db.add(crypto_detail)

        crypto_detail.rank = crypto_data.get("market_cap_rank")
        crypto_detail.circulating_supply = crypto_data.get("circulating_supply")
        crypto_detail.max_supply = crypto_data.get("max_supply")
        crypto_detail.total_supply = crypto_data.get("total_supply")
        crypto_detail.price_change_24h = crypto_data.get("price_change_24h")
        crypto_detail.price_change_percentage_24h = crypto_data.get("price_change_percentage_24h")
        crypto_detail.price_change_percentage_7d = crypto_data.get("price_change_percentage_7d")
        crypto_detail.price_change_percentage_14d = crypto_data.get("price_change_percentage_14d")
        crypto_detail.price_change_percentage_30d = crypto_data.get("price_change_percentage_30d")
        crypto_detail.price_change_percentage_60d = crypto_data.get("price_change_percentage_60d")
        crypto_detail.price_change_percentage_200d = crypto_data.get("price_change_percentage_200d")
        crypto_detail.price_change_percentage_1y = crypto_data.get("price_change_percentage_1y")
        crypto_detail.ath = crypto_data.get("ath")
        crypto_detail.ath_change_percentage = crypto_data.get("ath_change_percentage")
        crypto_detail.ath_date = crypto_data.get("ath_date")
        crypto_detail.atl = crypto_data.get("atl")
        crypto_detail.atl_change_percentage = crypto_data.get("atl_change_percentage")
        crypto_detail.atl_date = crypto_data.get("atl_date")
        crypto_detail.last_updated = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(asset)

        return asset

    async def sync_crypto_markets(self, per_page: int = 100) -> int:
        """مزامنة جميع العملات الرقمية من CoinGecko"""
        data = await self.fetch_crypto_markets(per_page=per_page)
        if not data:
            return 0

        count = 0
        for crypto in data:
            try:
                self.save_crypto_asset(crypto)
                count += 1
            except Exception as e:
                print(f"Error saving crypto {crypto.get('symbol')}: {e}")

        return count

    # ===== دوال للاستعلام =====
    def get_crypto_list(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """الحصول على قائمة العملات الرقمية مع أحدث الأسعار"""
        query = self.db.query(Asset).filter(
            Asset.asset_type == AssetType.CRYPTO,
            Asset.status == AssetStatus.ACTIVE
        )
        total = query.count()
        assets = query.offset(offset).limit(limit).all()

        result = []
        for asset in assets:
            latest_price = self.db.query(AssetPrice).filter(
                AssetPrice.asset_id == asset.id
            ).order_by(AssetPrice.timestamp.desc()).first()

            crypto_detail = self.db.query(CryptoDetail).filter(
                CryptoDetail.asset_id == asset.id
            ).first()

            result.append({
                "asset": asset,
                "price": latest_price,
                "detail": crypto_detail
            })

        return {
            "cryptos": result,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    def get_crypto_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """الحصول على عملة رقمية بواسطة الرمز مع تفاصيلها"""
        asset = self.db.query(Asset).filter(
            Asset.symbol == symbol.upper(),
            Asset.asset_type == AssetType.CRYPTO
        ).first()

        if not asset:
            return None

        latest_price = self.db.query(AssetPrice).filter(
            AssetPrice.asset_id == asset.id
        ).order_by(AssetPrice.timestamp.desc()).first()

        crypto_detail = self.db.query(CryptoDetail).filter(
            CryptoDetail.asset_id == asset.id
        ).first()

        return {
            "asset": asset,
            "price": latest_price,
            "detail": crypto_detail
        }