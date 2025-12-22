from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base  # We will define this next

# Create the Async Engine
# echo=True prints SQL queries to the terminal (great for debugging)
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create the Session Factory
# This is what generates new DB sessions for every request
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Dependency Function
# This is used by FastAPI's Depends() to give each route a session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session