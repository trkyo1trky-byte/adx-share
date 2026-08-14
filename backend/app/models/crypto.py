#نموذج العملات الرقمية
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base

class CryptoDetail(Base):
    __tablename__ = "crypto_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, unique=True)
    rank = Column(Integer, nullable=True)
    circulating_supply = Column(Numeric(20, 2), nullable=True)
    max_supply = Column(Numeric(20, 2), nullable=True)
    total_supply = Column(Numeric(20, 2), nullable=True)
    price_change_24h = Column(Numeric(20, 6), nullable=True)
    price_change_percentage_24h = Column(Numeric(10, 4), nullable=True)
    price_change_percentage_7d = Column(Numeric(10, 4), nullable=True)
    price_change_percentage_14d = Column(Numeric(10, 4), nullable=True)
    price_change_percentage_30d = Column(Numeric(10, 4), nullable=True)
    price_change_percentage_60d = Column(Numeric(10, 4), nullable=True)
    price_change_percentage_200d = Column(Numeric(10, 4), nullable=True)
    price_change_percentage_1y = Column(Numeric(10, 4), nullable=True)
    ath = Column(Numeric(20, 6), nullable=True)
    ath_change_percentage = Column(Numeric(10, 4), nullable=True)
    ath_date = Column(DateTime(timezone=True), nullable=True)
    atl = Column(Numeric(20, 6), nullable=True)
    atl_change_percentage = Column(Numeric(10, 4), nullable=True)
    atl_date = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    asset = relationship("Asset", back_populates="crypto_detail")