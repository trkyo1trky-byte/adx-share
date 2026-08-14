#إضافة روات العملات الرقمية
from fastapi import APIRouter
from . import auth, users, markets, crypto, trading

router = APIRouter(prefix="/api/v1")

# تسجيل الرووات
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(markets.router)
router.include_router(crypto.router)
router.include_router(trading.router) #إضافة روات التداول