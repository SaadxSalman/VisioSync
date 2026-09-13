import re
from time import perf_counter

from .config import settings
from .database import Database
from .schemas import PageHit


class Retriever:
    mode = "lexical-fallback"
    model = "local-grounded-fallback"

    def __init__(self, database: Database) -> None:
        self.database = database

    def search(self, query: str, top_k: int, document_ids: list[str] | None = None) -> tuple[list[PageHit], int]:
        started = perf_counter()
        terms = set(re.findall(r"[a-z0-9-]+", query.lower()))
        pages = self.database.search_pages(terms, min(top_k, settings.max_retrieval_pages), document_ids or [])
        hits = [PageHit(page=item["page_number"], score=round(min(.98, .42 + item["overlap"] / max(1, len(terms)) * .56), 2), title=f"Page {item['page_number']:02d} visual region", excerpt=re.sub(r"\s+", " ", item["text"])[:260] or "Visual page retained as image patches; no OCR text available.", document_id=item["document_id"], document_name=item["document_name"]) for item in pages]
        return sorted(hits, key=lambda hit: hit.score, reverse=True), round((perf_counter() - started) * 1000)

    def answer(self, query: str, hits: list[PageHit]) -> str:
        if not hits:
            return "No indexed page matched this question. Try a component tag, terminal number, alarm code, or document name."
        return f"Retrieved {len(hits)} visual regions for this question. The strongest evidence is on page {hits[0].page}, where the page layout and nearby labels should be inspected together."
