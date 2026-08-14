"""
Seed initial data: roles, exchanges, sectors, and assets
"""

from app.core.database import SessionLocal
from app.models.role import Role
from app.models.market import Exchange, Sector, Asset, AssetType, AssetStatus, ExchangeStatus

def seed_roles(db):
    roles = [
        {"name": "USER", "description": "Regular user"},
        {"name": "TRADER", "description": "Trader"},
        {"name": "SUPPORT", "description": "Support staff"},
        {"name": "EDITOR", "description": "Content editor"},
        {"name": "ANALYST", "description": "Financial analyst"},
        {"name": "MODERATOR", "description": "Moderator"},
        {"name": "ADMIN", "description": "System admin"},
        {"name": "SUPER_ADMIN", "description": "Super admin"},
    ]
    
    for role_data in roles:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
    db.commit()
    print("✅ Roles seeded")

def seed_exchanges(db):
    exchanges = [
        {"code": "DFM", "name_ar": "سوق دبي المالي", "name_en": "Dubai Financial Market", "country": "الإمارات", "currency": "AED"},
        {"code": "ADX", "name_ar": "سوق أبوظبي للأوراق المالية", "name_en": "Abu Dhabi Securities Exchange", "country": "الإمارات", "currency": "AED"},
        {"code": "TASI", "name_ar": "تداول السعودية", "name_en": "Tadawul", "country": "السعودية", "currency": "SAR"},
        {"code": "QE", "name_ar": "بورصة قطر", "name_en": "Qatar Exchange", "country": "قطر", "currency": "QAR"},
        {"code": "KSE", "name_ar": "بورصة الكويت", "name_en": "Kuwait Stock Exchange", "country": "الكويت", "currency": "KWD"},
    ]
    
    for ex_data in exchanges:
        existing = db.query(Exchange).filter(Exchange.code == ex_data["code"]).first()
        if not existing:
            exchange = Exchange(status=ExchangeStatus.ACTIVE, **ex_data)
            db.add(exchange)
    db.commit()
    print("✅ Exchanges seeded")

def main():
    db = SessionLocal()
    try:
        seed_roles(db)
        seed_exchanges(db)
        print("🎉 All seed data added successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()