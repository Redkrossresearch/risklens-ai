from fastapi import FastAPI, Depends, HTTPException
from fastapi import Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from auth import hash_password, verify_password, create_access_token
from upload import router as upload_router
from ticketing.routes import router as ticket_router
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="RiskLens AI")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(upload_router)
app.include_router(ticket_router)

class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "viewer"  # default viewer

class UserLogin(BaseModel):
    username: str
    password: str

users_db = {}  # { username: { "password": hashed, "role": role } }

@app.get("/")
def root():
    return {"message": "RiskLens AI is running"}

@app.post("/register")
def register(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    if user.role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    users_db[user.username] = {
        "password": hash_password(user.password),
        "role": user.role
    }
    return {"message": "User registered successfully", "role": user.role}

@app.post("/login")
def login(user: UserLogin):
    if user.username not in users_db:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(user.password, users_db[user.username]["password"]):
        raise HTTPException(status_code=400, detail="Incorrect password")
    token = create_access_token({
        "sub": user.username,
        "role": users_db[user.username]["role"]
    })
    return {"access_token": token, "token_type": "bearer", "role": users_db[user.username]["role"]}

from auth import get_role_from_token

@app.get("/admin/users")
def get_users(token: str):
    role = get_role_from_token(token)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return {"users": list(users_db.keys())}

@app.get("/analyst/vulnerabilities")  
def get_vulnerabilities(token: str):
    role = get_role_from_token(token)
    if role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"message": "Vulnerabilities accessible"}