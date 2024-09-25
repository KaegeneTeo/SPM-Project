from fastapi import FastAPI, Depends, Form, UploadFile, File, HTTPException, Request
from database import SessionLocal
from fastapi.encoders import jsonable_encoder
import crud, schemas,models
import uvicorn
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi import Body
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import binascii
#load_dotenv()


app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key='your_secret_key'
)  # Replace with your own secret key

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# To check the session details. If empty route to login.
@app.get("/session-check")
async def session_check(request: Request):
    # Check if session exists
    staff_id = request.session.get("staff_id")
    if staff_id:
        return {"authenticated": True, "staff_id": staff_id}
    return {"authenticated": False}

@app.get("/online")
def online():
    return {"status": "OK"}

# Get all employees
@app.get("/employees", response_model=list[schemas.EmployeeResponse])
def get_all_employees(db: Session = Depends(get_db)):
    result = crud.get_employees(db)
    if result == []:
        raise HTTPException(status_code=404, detail="No employees found.")
    return jsonable_encoder(crud.get_employees(db))

# Create employee
@app.post("/employees")
async def create_employee(employee: schemas.Employee, db: Session = Depends(get_db)):
    result = crud.create_employee(db, employee)
    if not result:    
        raise HTTPException(status_code=409, detail="Employee already exists.")
    return result


# Get employee by name
@app.get("/employees/{name}", response_model=schemas.EmployeeResponse)
async def get_employee_by_name(name: str, db: Session = Depends(get_db)):
    result = crud.get_employee_by_name(db, name)
    if result is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return jsonable_encoder(result)


@app.post("/login")
def login(request: Request, login: schemas.Login, db: Session = Depends(get_db)):
    # login = email & password
    print(login)
    user_result = crud.get_employee_by_email(db, login.email)
    if user_result is None:
        raise HTTPException(status_code=404, detail="User not found.")
    # login code here

    print(user_result.password_hash)
    bytes = hashlib.pbkdf2_hmac('sha256', login.email.encode('utf-8'), str(login.password).encode('utf-8'), 100000)
    hash = binascii.hexlify(bytes).decode()
    if not user_result.password_hash == hash:
        raise HTTPException(status_code=401, detail="Invalid password.")
    
    # Store the Staff_ID in the session
    request.session['staff_id'] = user_result.staff_id
    
    # Get the Team_ID(s) associated with the user's Staff_ID
    team_ids = crud.get_team_ids(db, user_result.staff_id)
    
    # Store the Team_ID(s) in the session
    request.session['team_ids'] = team_ids
    
    print("Session stored:", request.session)
    return jsonable_encoder({"message": "User logged in successfully.", 
                             "user": user_result, 
                             "team_ids": team_ids})

@app.post("/logout")
def logout(request: Request):
    # Clear the session (log out the user)
    request.session.clear()
    print("Session Cleared:", request.session)
    return {"message": "User logged out successfully."}

@app.post("/requests/")
def create_request(request: schemas.RequestCreate, db: Session = Depends(get_db)):
    db_request = models.Request(
        staff_id=request.staff_id,
        schedule_id=request.schedule_id,
        reason=request.reason,
        status=request.status,
        date=request.date,
        time_slot=request.time_slot,
        request_type=request.request_type,
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)  
    
    return db_request


@app.get("/team/requests", response_model=list[schemas.RequestResponse])
def get_requests_for_teams(request: Request, db: Session = Depends(get_db)):
    # Get all team_ids from the session
    print("Request received!")
    print(request.session)
    team_ids = request.session.get('team_ids')
    print(team_ids)
    
    # Check if team_ids exist in the session
    if not team_ids:
        raise HTTPException(status_code=404, detail="No team found for the logged-in user.")
        
    # Retrieve all Staff_IDs for the provided list of team_ids
    staff_ids = crud.get_staff_ids_by_team(db, team_ids)
    print(staff_ids)
    
    # Check if staff_ids list is empty and throw an error if no staff members are found
    if not staff_ids:
        raise HTTPException(status_code=404, detail="No staff found for the provided team IDs.")
    
    # Get all requests for the list of staff IDs
    requests = crud.get_requests_by_staff_ids(db, staff_ids)
    print(requests)
    
    # Check if requests are found, else throw an error message
    if not requests:
        raise HTTPException(status_code=404, detail="No requests found for staff members in these teams.")
    
    # Return the retrieved requests
    return jsonable_encoder(requests)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

