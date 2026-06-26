from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from auth import hash_password, verify_password, create_access_token

app = FastAPI(title="RiskLens AI")

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

users_db = {}

@app.get("/")
def root():
    return {"message": "RiskLens AI is running"}

@app.post("/register")
def register(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db[user.username] = hash_password(user.password)
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin):
    if user.username not in users_db:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(user.password, users_db[user.username]):
        raise HTTPException(status_code=400, detail="Incorrect password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}