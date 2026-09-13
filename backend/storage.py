import uuid
from pathlib import Path
from fastapi import UploadFile

from .config import settings


class FileStorage:
    def save_upload(self, file: UploadFile) -> tuple[Path, int]:
        safe_name = Path(file.filename or "document.pdf").name
        destination = settings.upload_dir / f"{uuid.uuid4()}-{safe_name}"
        total = 0
        with destination.open("wb") as output:
            while chunk := file.file.read(1024 * 1024):
                total += len(chunk)
                if total > settings.max_upload_mb * 1024 * 1024:
                    destination.unlink(missing_ok=True)
                    raise ValueError(f"File exceeds {settings.max_upload_mb} MB limit")
                output.write(chunk)
        return destination, total

    def document_dir(self, document_id: str) -> Path:
        path = settings.upload_dir / document_id
        path.mkdir(parents=True, exist_ok=True)
        return path
