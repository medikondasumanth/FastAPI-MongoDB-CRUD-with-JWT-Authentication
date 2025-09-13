from fastapi import FastAPI, HTTPException, status, Query, Depends
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from pymongo.errors import DuplicateKeyError
from datetime import timedelta

from db import employees_collection, users_collection, setup_schema
from schemas import EmployeeCreate, EmployeeUpdate, EmployeeOut
from auth import (
    Token, User, UserCreate, UserLogin,
    get_password_hash, verify_password, create_access_token,
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Employee API with JWT Authentication")

# Helpers
def employee_helper(doc):
    return {
        "id": str(doc["_id"]),
        "employee_id": doc["employee_id"],
        "name": doc["name"],
        "department": doc["department"],
        "salary": doc["salary"],
        "joining_date": doc["joining_date"],
        "skills": doc.get("skills", [])
    }

def user_helper(doc):
    return {
        "username": doc["username"],
        "email": doc.get("email"),
        "full_name": doc.get("full_name"),
        "disabled": doc.get("disabled", False)
    }

# Startup Event
@app.on_event("startup")
async def startup_event():
    await employees_collection.create_index("employee_id", unique=True)
    await users_collection.create_index("username", unique=True)
    await users_collection.create_index("email", unique=True)
    await setup_schema()

# Auth Endpoints
@app.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    if await users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "disabled": False
    }
    res = await users_collection.insert_one(user_data)
    new_user = await users_collection.find_one({"_id": res.inserted_id})
    return user_helper(new_user)

@app.post("/auth/login", response_model=Token)
async def login_for_access_token(user_credentials: UserLogin):
    user = await users_collection.find_one({"username": user_credentials.username})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Employee Endpoints
@app.post("/employees", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(emp: EmployeeCreate, current_user: User = Depends(get_current_active_user)):
    data = jsonable_encoder(emp)
    if await employees_collection.find_one({"employee_id": data["employee_id"]}):
        raise HTTPException(status_code=400, detail="employee_id already exists")
    res = await employees_collection.insert_one(data)
    new_doc = await employees_collection.find_one({"_id": res.inserted_id})
    return employee_helper(new_doc)

@app.get("/employees", response_model=List[EmployeeOut])
async def list_employees(
    department: Optional[str] = Query(None),
    page: int = 1,
    size: int = 50,
    current_user: User = Depends(get_current_active_user)
):
    query = {"department": department} if department else {}
    skip = (page - 1) * size
    cursor = employees_collection.find(query).sort("joining_date", -1).skip(skip).limit(size)
    return [employee_helper(doc) async for doc in cursor]

@app.get("/employees/avg-salary")
async def avg_salary_by_department(current_user: User = Depends(get_current_active_user)):
    pipeline = [
        {"$match": {"salary": {"$exists": True, "$type": "int"}, "department": {"$exists": True}}},
        {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}},
        {"$project": {"_id": 0, "department": "$_id", "avg_salary": {"$round": ["$avg_salary", 0]}}}
    ]
    cursor = employees_collection.aggregate(pipeline)
    results = []
    async for doc in cursor:
        results.append({"department": doc["department"], "avg_salary": doc["avg_salary"]})
    return {"data": results}

@app.get("/employees/search", response_model=List[EmployeeOut])
async def search_by_skill(skill: str, current_user: User = Depends(get_current_active_user)):
    cursor = employees_collection.find({"skills": skill}).sort("joining_date", -1)
    return [employee_helper(doc) async for doc in cursor]

@app.get("/employees/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id: str, current_user: User = Depends(get_current_active_user)):
    doc = await employees_collection.find_one({"employee_id": employee_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee_helper(doc)

@app.put("/employees/{employee_id}")
async def update_employee(employee_id: str, emp: EmployeeUpdate, current_user: User = Depends(get_current_active_user)):
    update_data = {k: v for k, v in emp.dict(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    res = await employees_collection.update_one({"employee_id": employee_id}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee updated"}

@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str, current_user: User = Depends(get_current_active_user)):
    res = await employees_collection.delete_one({"employee_id": employee_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted"}

# Root
@app.get("/")
async def root():
    return {"message": "Employee API with JWT Authentication", "status": "Active"}
