from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import settings
from .database import Database
from .ingestion import IngestionService
from .retrieval import Retriever
from .schemas import DocumentResponse, QueryRequest, QueryResponse
from .storage import FileStorage


database = Database(settings.database_path)
storage = FileStorage()
ingestion = IngestionService(database, storage)
retriever = Retriever(database)

app = FastAPI(title=settings.app_name, version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": settings.environment, "retrieval": retriever.mode, "documents": len(database.list_documents())}


@app.get("/documents", response_model=list[DocumentResponse])
def documents() -> list[dict]:
    return database.list_documents()


@app.get("/documents/{document_id}", response_model=DocumentResponse)
def document(document_id: str) -> dict:
    result = database.get_document(document_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return result


@app.get("/documents/{document_id}/pages/{page_number}/image")
def page_image(document_id: str, page_number: int) -> FileResponse:
    page = database.get_page(document_id, page_number)
    if not page or not Path(page["image_path"]).is_file():
        raise HTTPException(status_code=404, detail="Page image not found")
    return FileResponse(page["image_path"], media_type="image/jpeg", filename=f"{document_id}-page-{page_number}.jpg")


@app.post("/documents", response_model=DocumentResponse, status_code=201)
def upload_document(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported")
    try:
        source_path, size_bytes = storage.save_upload(file)
        return ingestion.ingest(source_path, file.filename, size_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not index PDF: {exc}") from exc


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    hits, latency_ms = retriever.search(request.query, request.top_k, request.document_ids)
    return QueryResponse(answer=retriever.answer(request.query, hits), hits=hits, model=retriever.model, retrieval_mode=retriever.mode, query=request.query, latency_ms=latency_ms)
