# TradeFlowAPI

**A High-Performance Async Investment Portfolio API**

TradeFlow is a RESTful API built with FastAPI and PostgreSQL that allows users to track stock portfolios, record buy/sell transactions, and view real-time performance metrics using live market data.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)

---

## Key Features

* **Real-Time ROI Calculation:** Aggregates transaction history to calculate weighted average cost basis and real-time profit/loss using live market data (Finhub API integration for stock price).
* **Asynchronous Architecture:** Utilizes Python's `asyncio` and `SQLAlchemy` async sessions for non-blocking database I/O.
* **Complex SQL Aggregations:** Normalized database schema designed to handle multi-portfolio management and historical transaction logging.
* **Security:** Full JWT Authentication flow (OAuth2) with password hashing (Bcrypt).
* **Containerized:** Fully Dockerized application and database for one-command deployment.

---

## Stack

* **Framework:** FastAPI (Python 3.10)
* **Database:** PostgreSQL 15
* **ORM:** SQLAlchemy 2.0 (Async Engine)
* **Validation:** Pydantic V2
* **External API:** https://finnhub.io
* **Deployment:** Docker & Docker Compose

---

## Database Schema

The project uses a normalized relational schema to ensure data integrity.

* **Users:** Stores authentication credentials.
* **Portfolios:** Links users to specific holdings (e.g., "Retirement", "Crypto").
* **Transactions:** An append-only ledger of all Buys and Sells.



---

## Getting Started

The project is configured with Docker Compose for an instant setup.

### Prerequisites
* Docker/Docker Compose installed.

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/ahmetallic/tradeflowapi]
    cd tradeflow
    ```

2.  **Run with Docker**
    ```bash
    docker-compose up --build
    ```

3.  **Access the API**
    * Open your browser to: `http://localhost:8000/docs`
    * This loads the **Swagger UI**, where you can test endpoints interactively.

---

## 📡 API Endpoints

### 1. Authentication
* `POST /auth/signup`: Create a new user.
* `POST /auth/login`: Get a JWT access token.

### 2. Portfolios
* `POST /portfolios`: Create a new portfolio bucket.
* `GET /portfolios`: List all user portfolios.

### 3. Transactions
* `POST /portfolios/{id}/transactions`: Record a Buy/Sell.
    * *Validation:* Checks for valid ticker symbols and non-negative quantities.

### 4. Analysis (The "Smart" Endpoint)
* `GET /portfolios/{id}/performance`:
    * Fetches all historical transactions.
    * Calculates current holdings (Net Shares).
    * Fetches live price from innhub.io.
    * Returns **Total Equity**, **Total Cost Basis**, and **ROI %**.

---

## Highlights

### Handling Synchronous External APIs
The `yfinance` library is synchronous (blocking). To prevent it from freezing the FastAPI async event loop, I utilized `run_in_executor` to offload external API calls to a separate thread pool.

### Dependency Injection
Database sessions and Current User authentication are injected into routes using FastAPI's `Depends`. This ensures that:
1.  Database connections are properly closed after every request.
2.  Unit tests can easily mock the database or user state.


---

## License

This project is licensed under the MIT License.
