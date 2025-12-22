from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator

# --- Transaction Schemas ---

class TransactionBase(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock Ticker Symbol (e.g. AAPL)")
    type: Literal['BUY', 'SELL']
    quantity: float = Field(..., gt=0, description="Must be greater than 0")
    price_per_share: float = Field(..., gt=0, description="Must be greater than 0")

    @field_validator('ticker')
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper()

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int
    portfolio_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Portfolio Schemas ---

class PortfolioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioRead(PortfolioBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


# --- User Schemas ---

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 chars")

class UserRead(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Performance / Analysis Schemas ---

class HoldingPerformance(BaseModel):
    ticker: str
    quantity: float
    avg_buy_price: float
    current_price: float
    current_value: float
    profit_loss: float
    profit_loss_pct: float

class PortfolioPerformance(BaseModel):
    portfolio_id: int
    total_value: float
    total_invested: float # Cost basis
    total_profit_loss: float
    total_roi_pct: float
    holdings: List[HoldingPerformance]