from pydantic import BaseModel
from datetime import datetime
from typing import List


class Employee(BaseModel):
    staff_id : int
    staff_fname : str
    staff_lname : str
    dept : str | None = None
    position : str
    country : str
    email : str
    reporting_manager : int | None = None
    role : str
    password: str
    password_hash: str | None = None

class EmployeeResponse(BaseModel):
    staff_id : int
    staff_fname : str
    staff_lname : str
    dept : str | None = None
    position : str
    country : str
    email : str
    reporting_manager : int | None = None
    role : str


class Login(BaseModel):
    email: str
    password: str