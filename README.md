# DIGI AATA E-Commerce Backend

Backend API for DIGI AATA Wooden Toys E-Commerce Platform

## Quick Start
# Windows
1.Create Virtual Environment (Windows)
2.python -m venv venv
3.venv\Scripts\activate
4.pip install -r requirements.txt
# Initialize Database
py -3 init_db.py
- Create all database tables
- Create admin user (admin@digiaata.com / admin123)
- Populate 6 categories
- Add 24 products
# Run Server
uvicorn app.main:app --reload


Server runs on: http://localhost:8000
API Docs: http://localhost:8000/docs

# Mac 

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

Last Updated: December 3, 2025

Added products url links to database and pushed to git 





Version: 1.0.0

1. Features

User Registration & Login (JWT Authentication)

Bcrypt-based secure password hashing

Products, Categories, Cart, Orders, and Address APIs

PostgreSQL relational database

FastAPI documentation (Swagger + ReDoc)

Clean modular project folder structure

2. Technologies Used
Component	Tech Stack
Backend API	FastAPI
Database	PostgreSQL 16
ORM	SQLAlchemy
Auth	JWT + Passlib Bcrypt
Server	Uvicorn
3. Prerequisites

Install the following:

Python 3.10+

PostgreSQL 14/15/16

Git

pip

4. Project Setup
Step 1 — Clone the repository
git clone <your-repo-url>
cd digiaata-main

Step 2 — Create & activate a virtual environment
python -m venv venvsource
venvsource\Scripts\activate

Step 3 — Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic
pip install "python-jose[cryptography]"
pip install "passlib[bcrypt]"
pip install python-multipart email-validator pydantic-settings dotenv

5. PostgreSQL Setup
Step 1 — Start PostgreSQL manually
"C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe" start -D "C:\PostgresData\data" -l "C:\PostgresData\logs\postgres.log"


Verify:

netstat -ano | findstr 5432

Step 2 — Create the database
psql -U postgres -c "CREATE DATABASE digi_aata;"

Step 3 — Set environment variables

Create .env in project root:

DATABASE_URL=postgresql+psycopg2://postgres:postgres123@localhost:5432/digi_aata
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

6. Run the Backend Server
python -m uvicorn app.main:app --reload


Open docs:

http://127.0.0.1:8000/docs

7. Database Troubleshooting & Fixes
FIX 1 — bcrypt error

You may see:

AttributeError: module 'bcrypt' has no attribute '__about__'


Solution:

pip uninstall passlib bcrypt -y
pip install bcrypt==4.0.1
pip install "passlib[bcrypt]"

FIX 2 — "id cannot be null" for users table

If inserting a user fails:

psycopg2.errors.NotNullViolation: null value in column "id"


Run this SQL:

CREATE SEQUENCE users_id_seq OWNED BY users.id;
ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq');
SELECT setval('users_id_seq', COALESCE((SELECT MAX(id)+1 FROM users), 1), false);

FIX 3 — Test manual user insert
INSERT INTO users (email,password_hash,full_name,phone,role,is_active,created_at)
VALUES ('test@example.com','hash','Test','000','user',true,now()) RETURNING id;

8. API Endpoints Summary
User APIs
Method	Endpoint	Description
POST	/api/auth/register	Register new user
POST	/api/auth/login	Login & receive JWT
GET	/api/users/me	Get logged-in user

Example registration:

{
  "email": "jyothi@example.com",
  "full_name": "Jyothi Test",
  "phone": "9999999999",
  "password": "StrongPass123"
}

9. Verify Registration Works

Successful response:

{
  "email": "jyothi@example.com",
  "full_name": "Jyothi Test",
  "phone": "9999999999",
  "id": 3,
  "role": "user",
  "is_active": true,
  "created_at": "2025-12-11T07:19:20.501368"
}

10. Folder Structure
app/
 ├── main.py
 ├── database.py
 ├── models/
 ├── routers/
 ├── schemas/
 ├── crud/
 ├── utils/
 └── config/
