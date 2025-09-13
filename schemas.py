from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., example="E123")
    name: str
    department: str
    salary: int
    joining_date: str  # YYYY-MM-DD
    skills: List[str] = []

    @validator("joining_date")
    def check_date(cls, v):
        if not DATE_RE.match(v):
            raise ValueError("joining_date must be YYYY-MM-DD")
        return v

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[int] = None
    joining_date: Optional[str] = None
    skills: Optional[List[str]] = None

    @validator("joining_date")
    def check_date(cls, v):
        if v and not DATE_RE.match(v):
            raise ValueError("joining_date must be YYYY-MM-DD")
        return v

class EmployeeOut(EmployeeCreate):
    id: str
