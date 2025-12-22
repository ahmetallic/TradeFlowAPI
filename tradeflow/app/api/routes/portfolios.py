from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models import Portfolio, User
from app.schemas import PortfolioCreate, PortfolioRead
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/portfolios")

@router.post("/", response_model=PortfolioRead, status_code=201)
async def create_portfolio(
    portfolio_in: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_portfolio = Portfolio(
        **portfolio_in.model_dump(),
        user_id=current_user.id
    )
    db.add(new_portfolio)
    await db.commit()
    await db.refresh(new_portfolio)
    return new_portfolio

@router.get("/", response_model=List[PortfolioRead])
async def read_portfolios(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Portfolio).where(Portfolio.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()