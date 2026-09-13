import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    pages INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL,
                    indexed_at TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL DEFAULT 0,
                    source_path TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    page_number INTEGER NOT NULL,
                    text TEXT NOT NULL DEFAULT '',
                    image_path TEXT NOT NULL,
                    UNIQUE(document_id, page_number)
                );
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    status TEXT NOT NULL,
                    progress INTEGER NOT NULL DEFAULT 0,
                    message TEXT NOT NULL DEFAULT ''
                );
            """)

    def list_documents(self) -> list[dict[str, Any]]:
        with self.connection() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM documents ORDER BY indexed_at DESC")]

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
            return dict(row) if row else None

    def create_document(self, values: dict[str, Any]) -> None:
        with self.connection() as connection:
            connection.execute("INSERT INTO documents (id, name, pages, status, indexed_at, kind, size_bytes, source_path) VALUES (:id, :name, :pages, :status, :indexed_at, :kind, :size_bytes, :source_path)", values)

    def update_document(self, document_id: str, **values: Any) -> None:
        assignments = ", ".join(f"{key} = ?" for key in values)
        with self.connection() as connection:
            connection.execute(f"UPDATE documents SET {assignments} WHERE id = ?", [*values.values(), document_id])

    def add_page(self, values: dict[str, Any]) -> None:
        with self.connection() as connection:
            connection.execute("INSERT OR REPLACE INTO pages (document_id, page_number, text, image_path) VALUES (:document_id, :page_number, :text, :image_path)", values)

    def search_pages(self, terms: set[str], limit: int, document_ids: list[str]) -> list[dict[str, Any]]:
        with self.connection() as connection:
            query = "SELECT pages.*, documents.name AS document_name FROM pages JOIN documents ON documents.id = pages.document_id WHERE documents.status = 'indexed'"
            values: list[str] = []
            if document_ids:
                placeholders = ",".join("?" for _ in document_ids)
                query += f" AND pages.document_id IN ({placeholders})"
                values.extend(document_ids)
            rows = connection.execute(query, values).fetchall()
        scored = []
        for row in rows:
            item = dict(row)
            import re
            page_terms = set(re.findall(r"[a-z0-9-]+", item["text"].lower()))
            overlap = len(terms & page_terms)
            if overlap:
                item["overlap"] = overlap
                scored.append(item)
        return sorted(scored, key=lambda item: item["overlap"], reverse=True)[:limit]

    def get_page(self, document_id: str, page_number: int) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM pages WHERE document_id = ? AND page_number = ?", (document_id, page_number)).fetchone()
            return dict(row) if row else None
