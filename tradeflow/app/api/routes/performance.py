from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx 
import asyncio

from app.core.config import settings
from app.db.session import get_db
from app.models import Portfolio, Transaction
from app.schemas import PortfolioPerformance, HoldingPerformance
from app.api.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/portfolios", tags=["Analysis"])

async def get_live_prices(tickers: List[str]) -> Dict[str, float]:
    """
    Fetches real-time prices from Finnhub.io
    Rate Limit: 60 calls/minute (Free Tier)
    """
    if not tickers:
        return {}
    
    prices = {}
    
    # Finnhub requires 1 call per ticker (no batching on free tier)
    # We use asyncio to fire them all in parallel for speed
    async with httpx.AsyncClient() as client:
        tasks = []
        for ticker in tickers:
            url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={settings.FINNHUB_API_KEY}"
            tasks.append(client.get(url))
        
        print(f" Calling Finnhub for: {tickers}")
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for ticker, response in zip(tickers, responses):
            if isinstance(response, Exception):
                print(f" Request failed for {ticker}: {response}")
                continue
                
            if response.status_code == 200:
                data = response.json()
                # Finnhub returns 'c' as the Current Price
                price = data.get('c', 0.0)
                if price > 0:
                    prices[ticker] = float(price)
                    print(f" {ticker}: ${price}")
                else:
                     print(f" {ticker} data invalid: {data}")
            elif response.status_code == 429:
                print("⏳ Rate Limit Exceeded (60 calls/min). Slow down.")
            else:
                print(f" Error {response.status_code} for {ticker}")

    return prices

@router.get("/{portfolio_id}/performance", response_model=PortfolioPerformance)
async def get_portfolio_performance(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch Portfolio
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # 2. Fetch Transactions
    result_tx = await db.execute(
        select(Transaction).where(Transaction.portfolio_id == portfolio_id)
    )
    transactions = result_tx.scalars().all()

    # 3. Aggregate Holdings
    holdings_map = {} 
    
    for tx in transactions:
        if tx.ticker not in holdings_map:
            holdings_map[tx.ticker] = {"qty": 0, "cost": 0.0}
        
        if tx.type == "BUY":
            holdings_map[tx.ticker]["qty"] += tx.quantity
            holdings_map[tx.ticker]["cost"] += (tx.quantity * tx.price_per_share)
        elif tx.type == "SELL":
            holdings_map[tx.ticker]["qty"] -= tx.quantity
            if holdings_map[tx.ticker]["qty"] > 0:
                avg_price = holdings_map[tx.ticker]["cost"] / (holdings_map[tx.ticker]["qty"] + tx.quantity)
                holdings_map[tx.ticker]["cost"] -= (tx.quantity * avg_price)
            else:
                holdings_map[tx.ticker]["cost"] = 0

    # 4. Get Live Prices
    tickers = list(holdings_map.keys())
    current_prices = await get_live_prices(tickers)

    # 5. Calculate Performance
    total_value = 0.0
    total_invested = 0.0
    holding_performances = []

    for ticker, data in holdings_map.items():
        qty = data["qty"]
        if qty <= 0:
            continue
            
        cost_basis = data["cost"]
        # Fallback to cost basis if API fails (0% P/L)
        fallback_price = cost_basis / qty if qty > 0 else 0
        current_price = current_prices.get(ticker, fallback_price)
        
        current_value = qty * current_price
        
        profit_loss = current_value - cost_basis
        profit_loss_pct = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0.0
        
        total_value += current_value
        total_invested += cost_basis
        
        holding_performances.append(HoldingPerformance(
            ticker=ticker,
            quantity=qty,
            avg_buy_price=cost_basis / qty if qty > 0 else 0,
            current_price=current_price,
            current_value=current_value,
            profit_loss=profit_loss,
            profit_loss_pct=profit_loss_pct
        ))

    total_profit_loss = total_value - total_invested
    total_roi_pct = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0.0

    return PortfolioPerformance(
        portfolio_id=portfolio.id,
        total_value=total_value,
        total_invested=total_invested,
        total_profit_loss=total_profit_loss,
        total_roi_pct=total_roi_pct,
        holdings=holding_performances
    )