from datetime import datetime, timezone
from pathlib import Path
import uuid
import fitz

from .config import settings
from .database import Database
from .storage import FileStorage


class IngestionService:
    def __init__(self, database: Database, storage: FileStorage) -> None:
        self.database = database
        self.storage = storage

    def ingest(self, source_path: Path, name: str, size_bytes: int) -> dict:
        document_id = str(uuid.uuid4())
        self.database.create_document({"id": document_id, "name": name, "pages": 0, "status": "processing", "indexed_at": datetime.now(timezone.utc).isoformat(), "kind": "PDF", "size_bytes": size_bytes, "source_path": str(source_path)})
        page_count = 0
        try:
            pdf = fitz.open(source_path)
            output_dir = self.storage.document_dir(document_id)
            for index, page in enumerate(pdf):
                page_number = index + 1
                image_path = output_dir / f"page-{page_number:04d}.jpg"
                pixmap = page.get_pixmap(matrix=fitz.Matrix(settings.render_scale, settings.render_scale), alpha=False)
                pixmap.save(image_path)
                self.database.add_page({"document_id": document_id, "page_number": page_number, "text": page.get_text("text").strip(), "image_path": str(image_path)})
                page_count = page_number
            self.database.update_document(document_id, pages=page_count, status="indexed")
        except Exception:
            self.database.update_document(document_id, status="failed")
            raise
        return self.database.get_document(document_id) or {}
