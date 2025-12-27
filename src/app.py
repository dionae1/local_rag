from services import UploadService, DBService

from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends

app = FastAPI()


class PDFRequest(BaseModel):
    file_path: str


class QueryRequest(BaseModel):
    question: str


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


@app.post("/query-gemini/")
def query_documents(request: QueryRequest, service: DBService = Depends(DBService)):
    results = service.gemini_answer(request.question)
    return {"results": results}


@app.post("/query-ollama/")
def query_documents_ollama(request: QueryRequest, service: DBService = Depends(DBService)):
    results = service.ollama_answer(request.question)
    return {"results": results}


@app.delete("/clear-database/")
def clear_database(service: DBService = Depends(DBService)):
    service.clear_database()
    return {"status": "Vector database cleared."}
