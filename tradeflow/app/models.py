from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base 

# 1. The User Model
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationship: One User has Many Portfolios
    portfolios: Mapped[List["Portfolio"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

# 2. The Portfolio Model
class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="portfolios")
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="portfolio", cascade="all, delete-orphan"
    )

# 3. The Transaction Model
class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(10), index=True)
    type: Mapped[str] = mapped_column(String(4))  # "BUY" or "SELL"
    
    quantity: Mapped[float] = mapped_column(Float) 
    price_per_share: Mapped[float] = mapped_column(Float)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id"))

    # Relationship
    portfolio: Mapped["Portfolio"] = relationship(back_populates="transactions")