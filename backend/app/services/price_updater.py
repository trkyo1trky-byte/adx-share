import asyncio
import httpx
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging
from decimal import Decimal
from ..core.database import SessionLocal
from ..models.market import Asset, AssetPrice, AssetStatus
from ..core.config import settings

logger = logging.getLogger(__name__)

async def fetch_real_price(symbol: str) -> float:
    """جلب السعر الحقيقي من Alpha Vantage أو Binance أو محاكاة"""
    try:
        if settings.MARKET_DATA_PROVIDER == "alphavantage":
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={settings.ALPHA_VANTAGE_API_KEY}"
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=10)
                data = resp.json()
                if "Global Quote" in data and "05. price" in data["Global Quote"]:
                    return float(data["Global Quote"]["05. price"])
        elif settings.MARKET_DATA_PROVIDER == "binance":
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=10)
                data = resp.json()
                if "price" in data:
                    return float(data["price"])
        else:
            # محاكاة (للتطوير)
            import random
            return round(random.uniform(10, 500), 2)
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return None

async def update_all_prices():
    """تحديث أسعار جميع الأصول النشطة"""
    db = SessionLocal()
    try:
        assets = db.query(Asset).filter(Asset.status == AssetStatus.ACTIVE).all()
        for asset in assets:
            price = await fetch_real_price(asset.symbol)
            if price:
                new_price = AssetPrice(
                    asset_id=asset.id,
                    price=Decimal(str(price)),
                    timestamp=datetime.now(timezone.utc),
                    source=settings.MARKET_DATA_PROVIDER,
                    is_stale=False
                )
                db.add(new_price)
                logger.debug(f"Updated price for {asset.symbol}: {price}")
        db.commit()
        logger.info(f"Updated prices for {len(assets)} assets")
    except Exception as e:
        logger.error(f"Error updating prices: {e}")
    finally:
        db.close()

def schedule_price_updates():
    """تشغيل جدولة تحديث الأسعار"""
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: asyncio.run(update_all_prices()),
        'interval',
        seconds=settings.PRICE_UPDATE_INTERVAL_SECONDS
    )
    scheduler.start()
    logger.info(f"Price update scheduler started (interval: {settings.PRICE_UPDATE_INTERVAL_SECONDS}s)")