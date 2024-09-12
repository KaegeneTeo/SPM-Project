import schemas
import requests
#import amqp_connection
import sys
import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from os import environ
from contextlib import asynccontextmanager
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi.middleware.cors import CORSMiddleware

connection = None
channel = None
exchangename = "generic_topic"
exchangetype = "topic"


# Initialize FastAPI app
app = FastAPI()
origins = [
    "http://localhost:5173",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_ms = environ.get("USER_MS_URL") or "http://localhost:8101/"
"""
{
  "username": "string",
  "email": "string",
  "password": "string",
  "telegram_id": "string",
  "telegram_tag": "string"
}
"""

@app.get("/online")
def online():
    return {"message": "Authentication is online."}

@app.post("/signup")
def signup(user: schemas.User):
    user.password_hash = generate_password_hash(user.password, method='pbkdf2:sha256')
    print(user)
    user_result = requests.post(user_ms + "users", json=jsonable_encoder(user))

    if int(user_result.status_code) > 300:
        raise HTTPException(status_code=user_result.status_code, detail=user_result.json()["detail"])
        #channel.basic_publish(exchange=exchangename, routing_key="signup.error", body=json.dumps(user))
    return jsonable_encoder({"message": "User created successfully.", "user": user_result.json()})

"""
{
  "username": "string",
  "password": "string"
}
"""
@app.post("/login")
def login(user: schemas.LoginUser):
    user_result = requests.get(user_ms + "users/" + user.username)
    print(user_result.json())
    if int(user_result.status_code) > 300:
        raise HTTPException(status_code=user_result.status_code, detail=user_result.json())
        #channel.basic_publish(exchange=exchangename, routing_key="login.error", body=json.dumps(user))
    user_result = user_result.json()
    if not check_password_hash(user_result["password_hash"], user.password):
        raise HTTPException(status_code=401, detail="Invalid password.")
    return jsonable_encoder({"message": "User logged in successfully.", "user": user_result})
