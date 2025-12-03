# DIGI AATA E-Commerce Backend

Backend API for DIGI AATA Wooden Toys E-Commerce Platform

## Quick Start

### 1. Create Virtual Environment
python3 -m venv venvsource venv/bin/activate # Mac/Linux### 2. Install Dependencies
pip install -r requirements.txt### 3. Initialize Database
python init_db.py
This will:
- Create all database tables
- Create admin user (admin@digiaata.com / admin123)
- Populate 6 categories
- Add 24 products

### 4. Run Server
uvicorn app.main:app --reload


Server runs on: http://localhost:8000
API Docs: http://localhost:8000/docs

## Project Structure
backend/├── app/│ ├── models/ # Database models│ ├── schemas/ # Pydantic schemas│ ├── routers/ # API endpoints│ ├── config.py # Configuration│ ├── database.py # Database connection│ └── main.py # FastAPI app├── tests/ # Test files├── uploads/ # Product images├── requirements.txt # Dependencies├── .env # Environment variables└── init_db.py # Database initialization
## API Endpoints

### Authentication
- POST `/api/auth/register` - Register user
- POST `/api/auth/login` - Login user
- GET `/api/auth/me` - Get current user

### Products
- GET `/api/products` - List all products
- GET `/api/products/{id}` - Get single product
- POST `/api/products` - Create product (admin)
- PUT `/api/products/{id}` - Update product (admin)
- DELETE `/api/products/{id}` - Delete product (admin)

### Categories
- GET `/api/categories` - List categories
- GET `/api/categories/{id}/products` - Get category products

### Cart
- GET `/api/cart` - Get user cart
- POST `/api/cart/items` - Add to cart
- PUT `/api/cart/items/{id}` - Update quantity
- DELETE `/api/cart/items/{id}` - Remove item

### Orders
- POST `/api/orders` - Create order
- GET `/api/orders` - Get user orders
- GET `/api/orders/{id}` - Get order details

### Admin
- GET `/api/admin/orders` - All orders
- GET `/api/admin/stats` - Dashboard stats

## Default Credentials

**Admin Account:**
- Email: admin@digiaata.com
- Password: admin123

Change in production!

## Testing

Use Swagger UI at http://localhost:8000/docs

## Team

- Backend Dev 1: Authentication & User Management
- Backend Dev 2: Products & Categories
- Backend Dev 3: Cart, Orders & Payment

---

Last Updated: November 24, 2025
Version: 1.0.0
