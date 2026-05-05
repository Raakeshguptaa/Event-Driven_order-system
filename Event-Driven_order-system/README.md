# Event-Driven Order System

A scalable, production-ready order management system built with asynchronous task processing, event-driven architecture, and enterprise-grade concurrency control.

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135%2B-009485?logo=fastapi&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.3%2B-37B24D?logo=celery&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-336791?logo=postgresql&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-FF4B4B?logo=streamlit&logoColor=white)

##  Overview

This project implements a robust order management system with real-time inventory tracking and asynchronous order processing. It demonstrates best practices for building scalable distributed systems including:

- **Event-Driven Architecture**: Asynchronous task processing using Celery
- **Concurrency Control**: Row-level locking for safe concurrent stock updates
- **Admin Authentication**: Secure API endpoints with header-based authentication
- **Real-time UI**: Interactive Streamlit dashboard for order and inventory management
- **RESTful API**: FastAPI backend with comprehensive endpoint documentation

##  Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (Frontend)              │
│           (Client & Admin Dashboard)                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ HTTP Requests
                 │
┌────────────────▼────────────────────────────────────────┐
│              FastAPI Backend (REST API)                 │
│  • Order Management                                     │
│  • Inventory Management                                 │
│  • Admin Routes with Authentication                     │
└────────────────┬────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼ Async Tasks            ▼ Sync Operations
┌──────────────┐        ┌──────────────┐
│   Celery     │        │  PostgreSQL  │
│   Worker     │        │  Database    │
│              │        │              │
└──────────────┘        └──────────────┘
    │
    └─ RabbitMQ (Message Broker)
```

##  Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend API** | FastAPI | REST API with async support |
| **Task Queue** | Celery | Asynchronous task processing |
| **Message Broker** | RabbitMQ | Message queue for Celery |
| **Database** | PostgreSQL | Persistent data storage |
| **Frontend** | Streamlit | Interactive dashboard UI |
| **Language** | Python 3.13+ | Core implementation |

##  Features

 **Order Management**
- Create and track orders
- Real-time order status

 **Inventory Management**
- Add, update, and delete products
- Real-time stock tracking
- Stock level validation

 **Asynchronous Processing**
- Non-blocking order processing
- Background stock updates
- Task retry mechanism with exponential backoff

 **Concurrency Safety**
- Row-level database locking (FOR UPDATE)
- Preventing race conditions
- Safe concurrent stock operations

 **Security**
- Admin authentication via API headers
- Environment-based secret management
- Secure database connections

 **Monitoring**
- Health check endpoints
- Celery task status tracking
- Comprehensive logging

##  Getting Started

### Prerequisites

- Python 3.13 or higher
- PostgreSQL 13 or higher
- RabbitMQ 3.8 or higher
- pip or uv package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/event-driven-order-system.git
cd event-driven-order-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# source venv/bin/activate   # On macOS/Linux
```

3. **Install dependencies**
```bash
pip install -e .
# Or using uv
uv pip install -e .
```

4. **Install additional requirements**
```bash
pip install celery[amqp] streamlit requests python-dotenv
```

### Configuration

1. **Create `.env` file** in the project root:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/order_system

# Admin Authentication
ADMIN_SECRET=your-secure-admin-secret-key

# Celery Configuration
CELERY_BROKER_URL=pyamqp://guest@localhost//
CELERY_RESULT_BACKEND=rpc://
```

2. **Set up PostgreSQL database**
```bash
psql -U postgres
CREATE DATABASE order_system;
\q
```

3. **Ensure RabbitMQ is running**
```bash
# Using Docker (recommended)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Or install locally and start the service
```

##  Running the Application

### Terminal 1: Start Celery Worker
```bash
celery -A celery_app worker --pool=solo --loglevel=info
```

### Terminal 2: Start FastAPI Backend
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3: Start Streamlit Frontend
```bash
streamlit run app.py
```

The application will be available at:
- **Streamlit UI**: http://localhost:8501
- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

##  Project Structure

```
event-driven-order-system/
├── main.py                    # FastAPI application entry point
├── celery_app.py             # Celery configuration
├── app.py                    # Streamlit frontend
├── pyproject.toml            # Project configuration & dependencies
├── .env                      # Environment variables (not in repo)
├── .gitignore               # Git ignore file
├── README.md                # This file
│
├── db/
│   └── database.py          # Database connection & utilities
│
├── inventory/
│   ├── model.py             # Inventory data models (Pydantic)
│   ├── inv_service.py       # Inventory business logic
│   └── inventory_db.py      # Inventory database operations
│
├── order/
│   └── model.py             # Order data models (Pydantic)
│
├── routes/
│   ├── __init__.py
│   └── admin.py             # Admin API endpoints & authentication
│
└── tasks/
    ├── __init__.py
    └── stock_tasks.py       # Celery async tasks for stock updates
```

##  API Endpoints

### Client Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/create_order` | Create a new order |
| GET | `/order` | Get all orders |

### Admin Endpoints (Requires Authentication)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/admin/` | Admin health check | ✗ |
| GET | `/admin/secure/` | Secure endpoint test | ✓ |
| GET | `/admin/secure/view_inventory` | List all inventory | ✓ |
| POST | `/admin/secure/add_inventory` | Add new product | ✓ |
| PUT | `/admin/secure/update_stock` | Update stock level | ✓ |
| DELETE | `/admin/secure/delete_inventory/{prod_id}` | Delete product | ✓ |

### Authentication

Admin endpoints require the `X-Admin-Secret` header:

```bash
curl -X GET http://localhost:8000/admin/secure/view_inventory \
  -H "X-Admin-Secret: your-admin-secret"
```

### Request/Response Examples

**Create Order**
```bash
POST /create_order
Content-Type: application/json

{
  "prod_id": 1,
  "prod_name": "Laptop",
  "prod_quant": 2
}
```

**Add Inventory**
```bash
POST /admin/secure/add_inventory
Content-Type: application/json
X-Admin-Secret: your-admin-secret

{
  "prod_name": "Laptop",
  "prod_quant": 100
}
```

##  Security Considerations

- Admin secret is stored in environment variables, not in code
- Row-level database locking prevents race conditions
- All database queries use parameterized statements (SQL injection prevention)
- Admin authentication on all sensitive endpoints
- Comprehensive error handling with appropriate HTTP status codes

##  Concurrency & Task Processing

### Stock Update Process
1. Client requests stock update via `/admin/secure/update_stock`
2. Request is immediately acknowledged with HTTP 200
3. Celery task is dispatched asynchronously
4. Celery worker picks up task from RabbitMQ queue
5. Row-level lock is acquired on the product
6. Stock is updated atomically
7. Lock is released and transaction is committed

### Benefits
- Non-blocking API responses
- Scalable task processing
- Safe concurrent operations
- Automatic retry on failure

##  Database Schema

### Inventory Table
```sql
CREATE TABLE inventory (
  product_id SERIAL PRIMARY KEY,
  product_name VARCHAR(100) NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 0
);
```

### Orders Table
```sql
CREATE TABLE orders (
  order_id SERIAL PRIMARY KEY,
  product_id INTEGER NOT NULL,
  product_name VARCHAR(100) NOT NULL,
  product_quantity INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##  Troubleshooting

### Issue: "Connection refused" to RabbitMQ
**Solution**: Ensure RabbitMQ is running and accessible on `localhost:5672`

### Issue: "Database connection failed"
**Solution**: 
1. Verify PostgreSQL is running
2. Check database credentials in `.env`
3. Ensure database exists: `CREATE DATABASE order_system;`

### Issue: Celery worker not processing tasks
**Solution**:
1. Check Celery worker terminal for errors
2. Verify RabbitMQ connection
3. Ensure `celery_app.py` imports are correct

### Issue: Streamlit connection errors
**Solution**: 
1. Verify FastAPI is running on `http://127.0.0.1:8000`
2. Check network connectivity
3. Review Streamlit logs

##  Performance Optimization

- Database indexing on frequently queried columns
- Connection pooling for database connections
- Task batching for bulk operations
- Row-level locking only during critical sections
- Async API handlers for non-blocking requests

##  Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use type hints in function signatures
- Add docstrings to functions and classes
- Write meaningful commit messages

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Author

Rakesh Kumar (@Raakeshguptaa)

##  Support

For support, email support@example.com or open an issue in the GitHub repository.

##  Related Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Last Updated**: May 2026  
**Version**: 0.1.0  
**Status**: Active Development
