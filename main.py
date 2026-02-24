from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from datetime import datetime, timedelta
from celery.result import AsyncResult
import pandas as pd
import os
import uuid

from tasks import train_model
from database import SessionLocal, Training

SECRET_KEY = "secret"
ALGORITHM = "HS256"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

fake_user = {"username": "admin", "password": "admin"}

UPLOAD_FOLDER = "uploads"
MODEL_FOLDER = "models"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

@app.post("/login")
def login(data: dict):
    if data["username"] == fake_user["username"] and data["password"] == fake_user["password"]:
        token = jwt.encode(
            {"sub": data["username"], "exp": datetime.utcnow() + timedelta(hours=1)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    df = pd.read_csv(path)
    return {"filename": filename, "columns": list(df.columns)}

@app.post("/train")
def train(data: dict, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload["sub"]

    task = train_model.delay(data["filename"], data["target"])

    db = SessionLocal()
    record = Training(username=username, model_type="auto", task_id=task.id)
    db.add(record)
    db.commit()
    db.close()

    return {"task_id": task.id}

@app.get("/results/{task_id}")
def results(task_id: str):
    result = AsyncResult(task_id)
    return {"status": result.status, "result": result.result}

@app.get("/dashboard")
def dashboard(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload["sub"]

    db = SessionLocal()
    records = db.query(Training).filter(Training.username == username).all()
    db.close()

    return [{"task_id": r.task_id} for r in records]

@app.get("/download/{filename}")
def download(filename: str):
    return FileResponse(f"{MODEL_FOLDER}/{filename}", filename=filename)