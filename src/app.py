from services import UploadService, LLMService, DBService, build_llm

from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

import os
model = os.getenv("LLM_MODEL", "dummy")
llm = build_llm(model)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "http://0.0.0.0",
    "http://0.0.0.0:8002",
    "http://127.0.0.1",
    "http://127.0.0.1:8002"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PDFRequest(BaseModel):
    file_path: str


class QueryRequest(BaseModel):
    question: str


@app.post("/upload-file/")
def upload_file(file: UploadFile):
    print("Received file:", file.filename)
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_file_path = Path(f"/tmp/{file.filename}")
    with temp_file_path.open("wb") as buffer:
        buffer.write(file.file.read())
        
    service = UploadService(str(temp_file_path))
    service.insert_documents()
    temp_file_path.unlink()
    return {"status": "Documents inserted into the vector database."}


@app.post("/upload/")
def upload_document(request: PDFRequest):
    file_path = Path((request.file_path)).expanduser().resolve()
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=400, detail="File does not exist.")

    if not file_path.suffix.lower() == ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    service = UploadService(str(file_path))
    service.insert_documents()
    return {"status": "Documents inserted into the vector database."}


@app.post("/query/")
def query_llm(request: QueryRequest):
    service = LLMService(llm)
    results = service.answer(request.question)
    return {"results": results}


@app.delete("/database/")
def clear_database(service: DBService = Depends(DBService)):
    service.clear_database()
    return {"status": "Vector database cleared."}


@app.get("/database/")
def is_database_empty(service: DBService = Depends(DBService)):
    empty = service.check_empty()
    return {"is_empty": empty}