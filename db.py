from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "assessment_db")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
employees_collection = db["employees"]
users_collection = db["users"]

# Schemas
employee_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["employee_id", "name", "department", "salary", "joining_date"],
        "properties": {
            "employee_id": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "department": {"bsonType": "string"},
            "salary": {"bsonType": "int"},
            "joining_date": {
                "bsonType": "string",
                "pattern": r"^\d{4}-\d{2}-\d{2}$"
            },
            "skills": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            }
        }
    }
}

user_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["username", "email", "full_name", "hashed_password"],
        "properties": {
            "username": {"bsonType": "string"},
            "email": {"bsonType": "string"},
            "full_name": {"bsonType": "string"},
            "hashed_password": {"bsonType": "string"},
            "disabled": {"bsonType": "bool"}
        }
    }
}

async def setup_schema():
    """Create collections with schema validation if they don't exist."""
    for collection_name, schema in [("employees", employee_schema), ("users", user_schema)]:
        try:
            await db.command({
                "collMod": collection_name,
                "validator": schema,
                "validationLevel": "strict"
            })
        except Exception:
            # Collection doesn't exist; create with schema
            await db.create_collection(collection_name, validator=schema)
    print("Database schemas setup successfully")
