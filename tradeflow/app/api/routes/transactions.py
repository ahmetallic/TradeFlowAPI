from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

# Import your local modules (adjust paths as needed)
from app.db.session import get_db
from app.models import Transaction, Portfolio, User
from app.schemas import TransactionCreate, TransactionRead
from app.api.dependencies import get_current_user # Assuming you have auth set up

router = APIRouter()

@router.post(
    "/portfolios/{portfolio_id}/transactions", 
    response_model=TransactionRead, 
    status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    portfolio_id: int,
    transaction_in: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a new buy/sell transaction.
    
    Checks:
    1. Does the portfolio exist?
    2. Does the portfolio belong to the logged-in user?
    """
    
    # 1. Fetch the Portfolio ensuring it belongs to the user
    # We use a specific SELECT statement to filter by both ID and Owner
    query = select(Portfolio).where(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    )
    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Portfolio not found or access denied"
        )

    # 2. Create the ORM Object
    # We unpack the Pydantic model (**transaction_in.model_dump()) 
    # and map it to the SQLAlchemy model.
    new_transaction = Transaction(
        **transaction_in.model_dump(),
        portfolio_id=portfolio_id
    )

    # 3. Add to DB and Commit
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction) # Refresh to get the generated ID and timestamp

    return new_transaction