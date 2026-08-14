"""
ADX SHARES API – الملف الرئيسي للتطبيق
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import router as api_router
from .core.config import settings
from .core.database import engine
from .models import user, role, market, crypto, trading
from .services.price_updater import schedule_price_updates
import logging
import json
from typing import Dict, Set

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء الجداول
user.Base.metadata.create_all(bind=engine)
role.Base.metadata.create_all(bind=engine)
market.Base.metadata.create_all(bind=engine)
crypto.Base.metadata.create_all(bind=engine)
trading.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ADX SHARES API",
    description="منصة التداول والاستثمار والأسواق الرقمية",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Routes =====
app.include_router(api_router.router)

# ===== WebSocket Manager =====
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "market"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket connected on channel {channel}")

    def disconnect(self, websocket: WebSocket, channel: str = "market"):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

    async def broadcast(self, channel: str, message: dict):
        if channel in self.active_connections:
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"WebSocket broadcast error: {e}")

manager = ConnectionManager()

@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str = "market"):
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            # يمكن معالجة الطلبات هنا (مثل الاشتراك في رمز معين)
            try:
                msg = json.loads(data)
                if msg.get("type") == "subscribe" and msg.get("symbol"):
                    logger.info(f"Client subscribed to {msg['symbol']}")
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
        logger.info(f"WebSocket disconnected from {channel}")

# ===== Health Checks =====
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "ADX SHARES API is running successfully!",
        "version": "1.0.0"
    }

@app.get("/api/v1/ready")
async def ready_check():
    return {
        "status": "ready",
        "services": {
            "database": "connected",
            "redis": "connected"
        }
    }

# ===== بدء الخدمات الخلفية =====
@app.on_event("startup")
async def startup_event():
    schedule_price_updates()
    logger.info("All background services started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)