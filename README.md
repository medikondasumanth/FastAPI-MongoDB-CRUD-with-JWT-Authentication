# FastAPI MongoDB CRUD with JWT Authentication

This project is a **FastAPI** application with **MongoDB** integration that provides complete **CRUD operations** (Create, Read, Update, Delete) with **JWT-based authentication**.

---

## 🚀 Features
- User authentication with **JWT tokens** (login required for protected routes).
- Passwords hashed securely using **Passlib**.
- CRUD operations on MongoDB collections.
- Built-in API documentation with **Swagger UI** (`/docs`) and **ReDoc** (`/redoc`).
- Environment variable management using `.env`.

---

## 📂 Project Structure
├── main.py # FastAPI application entry point
├── auth.py # JWT authentication & password hashing
├── database.py # MongoDB connection setup
├── models.py # Pydantic models for validation
├── routes.py # API routes for CRUD operations
├── requirements.txt # Python dependencies
├── .env # Environment variables (DB_URI, SECRET_KEY, etc.)
└── README.md # Project documentation

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/fastapi-mongodb-crud.git
cd fastapi-mongodb-crud

## Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

### 3️⃣ Install Dependencies
pip install -r requirements.txt

###4️⃣ Configure Environment Variables
Create a .env file in the project root:
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=mydatabase
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

5️⃣ Run the Application
uvicorn main:app --reload
The server will start at:
http://127.0.0.1:8000

🔑 Authentication Workflow

Register a new user
POST /register

Login to get JWT token
POST /login → returns access_token

Authorize requests
Click on the "Authorize" button in Swagger UI (/docs) and paste the token:

Bearer your_jwt_token

Access protected CRUD endpoints
Example routes:
POST /items/ → Create item
GET /items/ → List all items
GET /items/{id} → Get single item
PUT /items/{id} → Update item
DELETE /items/{id} → Delete item

📘 API Documentation
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

🛠️ Tech Stack

FastAPI – Web framework
MongoDB – Database
Motor – Async MongoDB driver
Passlib – Password hashing
Python-Jose – JWT authentication
Pydantic – Data validation
