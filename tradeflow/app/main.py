import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import engine, Base
from app.api.routes import auth, portfolios, transactions, performance

# --- Lifecycle Event ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables with Retry Logic
    # We try 5 times, waiting 2 seconds between attempts
    retries = 5
    while retries > 0:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print(" Database connected and tables created!")
            break
        except Exception as e:
            retries -= 1
            print(f" Database not ready yet ({e}). Retrying in 2s...")
            if retries == 0:
                print("Could not connect to database after 5 attempts.")
                raise e
            await asyncio.sleep(2)
    
    yield
    # Shutdown logic (if any) goes here

app = FastAPI(
    title="TradeFlow API", 
    version="1.0.0",
    lifespan=lifespan
)

# --- Include Routers ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(portfolios.router, tags=["Portfolios"])
app.include_router(transactions.router, tags=["Transactions"])
app.include_router(performance.router, tags=["Analysis"])

@app.get("/")
def root():
    return {"message": "TradeFlow API is running"}