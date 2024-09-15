from fastapi import FastAPI, Depends, Form, UploadFile, File, HTTPException
from database import SessionLocal
from fastapi.encoders import jsonable_encoder
import crud, schemas
from typing import Optional
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from telebot.async_telebot import AsyncTeleBot
import os
from contextlib import asynccontextmanager
import boto3
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import json
from fastapi import Body

load_dotenv()


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

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
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/online")
def online():
    return {"status": "OK"}

# Get all users
@app.get("/users", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    result = crud.get_users(db)
    if result == []:
        raise HTTPException(status_code=404, detail="No users found.")
    return jsonable_encoder(crud.get_users(db))

# Create user
@app.post("/users")
async def create_user(user: schemas.User, db: Session = Depends(get_db)):
    result = crud.create_user(db, user)
    if not result:    
        raise HTTPException(status_code=409, detail="User already exists.")
    return result


# Get user by username
@app.get("/users/{username}", response_model=schemas.UserResponse)
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    result = crud.get_user_by_username(db, username)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return jsonable_encoder(result)

# Get user by telegram tag
@app.get("/users/telegram/{telegram_tag}", response_model=schemas.UserResponse)
async def get_user_by_telegram_tag(telegram_tag: str, db: Session = Depends(get_db)):
    tag = "@" + telegram_tag
    
    result = crud.get_user_by_telegram_tag(db, tag)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return jsonable_encoder(result)

def upload_file(files: UploadFile, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    print("\n Uploading file to S3 bucket")
    print(files)
    # Upload the file
    if object_name is None:
        object_name = files.filename
        
    s3_client = boto3.client('s3', 
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY)
    try:
     
        s3_client.upload_fileobj(files.file, "spickbucket", object_name)
        
        return JSONResponse(status_code=200, content={"message": "File uploaded successfully."})
    except:
        return JSONResponse(status_code=400, content={"message": "File upload failed."})
# Update user information
@app.put("/users/user_id/{user_id}")
async def update_user(user_id: int, user: str = Form(...), files: Optional[UploadFile] = File(default=None), db: Session = Depends(get_db)):
    print(user)
    print(files)

    user = json.loads(user)
    user = schemas.User(**user)

    result = crud.update_user(db, user, user_id)
    if files:
        upload_file(files)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return result


# Update user password
@app.put("/users/user_id/{user_id}/password")
async def update_user_password(user_id: int, user: schemas.User, db: Session = Depends(get_db)):
    
    result = crud.update_user_password(db, user, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return result

# Update user telegram_id
@app.put("/users/telegram/{user_id}")
async def update_user_password(user_id: int, user: schemas.User, db: Session = Depends(get_db)):
    
    result = crud.update_user(db, user, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return result


# Get user by user_id
@app.get("/users/user_id/{user_id}", response_model=schemas.UserResponse)
async def get_user_by_user_id(user_id: int, db: Session = Depends(get_db)):
    result = crud.get_user_by_user_id(db, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return jsonable_encoder(result)
