# main.py
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import csv
import os

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/uploadfile/")
async def create_upload_file(request: Request, file: UploadFile = Form(...), name_col: int = Form(...), age_col: int = Form(...)):
    content = await file.read()
    decoded_content = content.decode("utf-8").splitlines()
    
    # Assume the CSV has headers, and we extract data accordingly
    csv_reader = csv.reader(decoded_content)
    headers = next(csv_reader)

    name_index = name_col - 1
    age_index = age_col - 1

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    for row in csv_reader:
        name = row[name_index]
        age = int(row[age_index])

        db_user = User(name=name, age=age)
        db.add(db_user)

    db.commit()
    db.close()

    return {"file_size": len(content), "name_col": headers[name_index], "age_col": headers[age_index]}
