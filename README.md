# VisioSync

## Multimodal, layout-aware RAG for engineering documents

VisioSync is a full-stack reference application for asking grounded questions across technical PDFs without destroying the visual structure that makes engineering documents useful. It is designed for schematics, panel wiring, P&IDs, datasheets, control sequences, alarm matrices, and other pages where meaning is encoded by proximity, line routing, symbols, tables, and diagram topology.

A conventional document pipeline extracts text, chunks paragraphs, embeds the chunks, and sends retrieved text to a language model. That is often the wrong representation for engineering pages. A wire that crosses a page, a table row aligned with a terminal number, or a symbol connected to an interlock can be more important than the words extracted around it. VisioSync therefore treats the rendered page image as the primary retrieval object.

## What is included

- **Next.js App Router frontend** with a dense engineering-console interface.
- **FastAPI backend** with health, upload, document listing, and query endpoints.
- **PyMuPDF ingestion** that validates PDFs, renders every page to an image, and records page-level metadata.
- **Visual retrieval boundary** ready for ColPali late-interaction embeddings and Weaviate storage.
- **Local fallback mode** that works without a GPU, model download, vector database, or API key. Uploaded PDFs can still be indexed and queried using page text as a deterministic development fallback.
- **Grounded answer contract** returning an answer, evidence pages, similarity scores, document IDs, and the active model/retriever name.
- **Docker Compose** for Weaviate and the Python API.
- **One root `.env`** for all runtime values. The file is ignored by Git; `.env.example` is safe to commit.

## Product flow

1. A user uploads a PDF from the web console.
2. FastAPI stores the file and opens it with PyMuPDF.
3. Each page is rendered at a stable resolution. The page image is retained as the canonical visual artifact.
4. In production, a ColPali-compatible late-interaction encoder produces patch-level page embeddings. The patch vectors are stored in Weaviate with document, page, image path, and bounding-region metadata.
5. A user question is encoded and compared against the page patch vectors. Top pages and regions are selected without converting the complete page into an OCR transcript.
6. The answer model receives the question plus only the selected page images or crops. It responds with a concise answer and source-page references.
7. The frontend renders the answer next to a retrieval trace so an engineer can inspect the evidence instead of trusting an opaque response.

## Repository layout

```text
VisioSync/
├── app/
│   ├── globals.css       # Visual system and responsive console layout
│   ├── layout.tsx        # Metadata and root shell
│   └── page.tsx          # Query, upload, corpus, and evidence UI
├── backend/
│   ├── Dockerfile        # Production-ish API image
│   ├── config.py          # Typed environment configuration
│   ├── database.py        # SQLite document/page metadata repository
│   ├── ingestion.py       # PDF rendering and indexing service
│   ├── main.py            # Thin FastAPI composition root and routes
│   └── requirements.txt   # Python runtime dependencies
├── app/components/       # Reusable query, evidence, corpus, and header UI
├── app/lib/              # Typed API client and shared frontend contracts
├── .env                 # Local secrets/configuration, ignored by Git
├── .env.example         # Documented configuration template
├── docker-compose.yml    # Weaviate + API local services
├── next.config.ts
├── package.json
└── README.md
```

## Prerequisites

For the simplest local demo:

- Node.js 20 or newer
- npm 10 or newer
- Python 3.11 or newer
- A PDF to test ingestion

For the vector-backed multimodal deployment:

- Docker Desktop with at least 8 GB RAM available
- A CUDA-capable GPU is strongly recommended for ColPali inference
- Enough disk space for model weights, rendered pages, and the Weaviate volume
- An OpenAI-compatible vision model key if you want generated narrative answers instead of the deterministic local response

## Local setup

The checked-in `.env` contains blank optional secrets and local defaults. Never add real credentials to Git. The `.gitignore` excludes `.env`, uploads, Python caches, and build output.

### 1. Install frontend dependencies

```powershell
npm install
```

### 2. Create a Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

### 3. Start the API

```powershell
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive OpenAPI documentation is at `http://localhost:8000/docs`.

### 4. Start the frontend

In another terminal:

```powershell
npm run dev
```

Open `http://localhost:3000`.

The frontend intentionally remains useful if the API is offline: it displays a local demo corpus and a representative grounded answer, then switches to live data automatically when the API becomes available.

## Docker setup

To start Weaviate and the API together:

```powershell
docker compose up --build
```

The API remains at `http://localhost:8000`; Weaviate is exposed at `http://localhost:8080`. Start the Next.js frontend locally with `npm run dev`, or add a frontend container when deploying behind a reverse proxy.

The Compose file uses anonymous Weaviate access for local development only. Configure authentication, TLS, backups, and a private network before using it with real engineering documents.

## API reference

### `GET /health`

Returns API and retrieval status.

```json
{
  "status": "ok",
  "retrieval": "indexed-pages"
}
```

### `GET /documents`

Returns indexed documents. Each document includes an ID, original filename, page count, indexing status, timestamp, and a broad document kind.

### `POST /documents`

Multipart upload endpoint. The form field must be named `file`, and the file must have a `.pdf` extension.

```powershell
curl -F "file=@./samples/panel.pdf" http://localhost:8000/documents
```

The initial implementation renders every page to JPEG under `UPLOAD_DIR`. This gives the multimodal pipeline a stable artifact immediately, even before a ColPali model is installed.

### `POST /query`

Accepts a question and a result count:

```json
{
  "query": "Where does the low-pressure alarm interlock with the supply fan?",
  "top_k": 6
}
```

The response includes `answer`, `hits`, `model`, and the original `query`. Each hit includes `page`, `score`, `title`, `excerpt`, `document_id`, and an optional `image_url`.

## ColPali and late-interaction integration

The current checked-in runtime deliberately has no heavyweight model dependency. That makes the repository quick to install and keeps CPU-only development practical. The retrieval boundary is page-oriented so a ColPali adapter can be introduced without changing the HTTP contract or the frontend.

A production adapter should:

1. Render each PDF page at the resolution expected by the selected ColPali checkpoint.
2. Run the processor/model to obtain patch embeddings for the complete page image.
3. Store the patch vectors and page metadata in Weaviate. Keep the page image path and page number beside the vector object.
4. At query time, encode the text query with the same processor, calculate the late-interaction MaxSim score against patch vectors, and retain the top pages plus their highest-scoring patch regions.
5. Persist normalized crop coordinates so the API can return evidence crops or construct them on demand.
6. Pass the selected images/crops to the vision-language model with an instruction to answer only from visible evidence and cite page numbers.

Do not reduce a page to one averaged vector if layout fidelity is the reason for using ColPali. The key benefit is late interaction between query tokens and page patch tokens.

## Weaviate collection guidance

Use a collection such as `VisioSyncPagePatch` with fields similar to:

- `document_id`: stable UUID
- `document_name`: original filename
- `page_number`: integer
- `image_path`: object storage or local artifact reference
- `crop_x`, `crop_y`, `crop_width`, `crop_height`: normalized region coordinates
- `content_hash`: ingestion deduplication key
- `embedding_model`: model/checkpoint identifier
- `created_at`: ingestion timestamp

Keep tenant or workspace IDs in the object properties if multiple teams will use one cluster. Engineering documents can contain sensitive infrastructure information; access control and document-level filtering are part of retrieval correctness, not an afterthought.

## Environment variables

All runtime configuration belongs in the root `.env`:

| Variable | Purpose | Default |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Browser-visible API base URL | `http://localhost:8000` |
| `CORS_ORIGINS` | Comma-separated allowed browser origins | `http://localhost:3000` |
| `UPLOAD_DIR` | Rendered pages and uploaded PDFs | `./uploads` |
| `WEAVIATE_URL` | Vector database URL | `http://localhost:8080` |
| `WEAVIATE_API_KEY` | Optional Weaviate key | empty |
| `COLPALI_MODEL` | Late-interaction checkpoint | `vidore/colpali-v1.2` |
| `EMBEDDING_DEVICE` | `auto`, `cpu`, or CUDA device | `auto` |
| `OPENAI_API_KEY` | Optional answer-model key | empty |
| `OPENAI_MODEL` | Vision-language answer model | `gpt-4o-mini` |
| `MAX_RETRIEVAL_PAGES` | Maximum evidence pages | `6` |

The current local API reads the upload and OpenAI settings. The remaining settings are reserved for the model/vector adapter and are intentionally already documented in the same file.

## Current runtime architecture

The backend is intentionally split into small replaceable pieces:

- `config.py` owns environment parsing and directory preparation.
- `storage.py` owns safe upload naming, streaming writes, and upload limits.
- `database.py` owns SQLite schema creation and document/page queries. The repository can later be replaced by Postgres without changing the HTTP routes.
- `ingestion.py` owns PyMuPDF work. It creates a document record, renders page images into a document-specific directory, stores page text as a secondary signal, and marks the document `indexed` or `failed`.
- `retrieval.py` owns the retrieval interface. Its current implementation is deterministic lexical fallback; a ColPali/Weaviate implementation can replace it while preserving `search()` and `answer()` behavior.
- `main.py` only composes dependencies and exposes the API contract.

This separation matters for scale. PDF rendering is CPU and I/O heavy, retrieval is model and vector-store heavy, and answer generation is network-bound. They should not become one request handler. The next production step is to put `IngestionService.ingest()` behind a queue worker while keeping the same database status fields and adding a job table or external task broker.

## Persistent data model

The local implementation creates `data/visiosync.db` and stores:

- One `documents` row per uploaded PDF, including status, page count, source path, size, and indexing timestamp.
- One `pages` row per rendered page, including the extracted secondary text and canonical JPEG path.
- A unique `(document_id, page_number)` constraint to keep retries idempotent at page level.

Rendered page images are stored under `uploads/<document-id>/page-0001.jpg`. The API exposes those artifacts through `GET /documents/{document_id}/pages/{page_number}/image`, which gives the future VLM and frontend a stable evidence URL rather than leaking filesystem paths.

## Extended API surface

- `GET /documents/{document_id}` returns one document or `404`.
- `GET /documents/{document_id}/pages/{page_number}/image` streams the rendered JPEG evidence page.
- `POST /query` accepts optional `document_ids` so a workspace can scope retrieval to selected documents.
- `GET /health` reports the environment, retrieval mode, and persistent document count.

The response contract includes `retrieval_mode`, `model`, and `latency_ms`. Those fields make it possible to compare fallback retrieval, ColPali retrieval, and hosted answer models in observability dashboards without changing the frontend.

## Scaling from local to production

1. Replace SQLite with Postgres for concurrent workers and durable metadata transactions.
2. Move source PDFs and rendered images to object storage. Keep only signed object references in the database.
3. Add a queue such as Redis-backed RQ, Celery, or a managed task system. Upload should return a job ID quickly, while a worker updates `processing`, `indexed`, and `failed` states.
4. Implement `Retriever` as a protocol-backed ColPali adapter. Store patch vectors and normalized crop coordinates in Weaviate, with a workspace/document filter applied before similarity scoring.
5. Add a separate answer service that sends only selected crops/pages to a vision-language model and requires page citations in the response schema.
6. Add authentication and workspace authorization before exposing document IDs, page images, or query traces.
7. Add metrics for upload duration, pages per document, render failures, retrieval latency, page recall at K, answer citation accuracy, and unsupported-claim rate.

## Testing

The backend has lightweight API contract tests in `backend/tests/test_api.py`. Run them with:

```powershell
C:/Python314/python.exe -m unittest discover -s backend/tests -p "test_*.py"
```

The tests intentionally focus on the stable external contract: health, query shape, and upload validation. Add fixture PDFs and ingestion tests when your repository has approved sample engineering documents.

## Verification

Backend syntax check:

```powershell
python -m compileall backend
```

Frontend typecheck/build:

```powershell
npm run build
```

API smoke test:

```powershell
curl http://localhost:8000/health
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d "{\"query\":\"supply fan alarm\",\"top_k\":2}"
```

## Production hardening checklist

- Put the API and frontend behind HTTPS.
- Replace anonymous Weaviate access with authentication and network policy.
- Add workspace/document authorization to every list, upload, query, and image route.
- Move PDF and page images to encrypted object storage.
- Add malware scanning and file-size/page-count limits before parsing.
- Use content hashes to deduplicate documents and make indexing idempotent.
- Add background jobs for large PDFs rather than holding an HTTP request open.
- Track model checkpoint versions so retrieval results can be reproduced.
- Store query traces with user, workspace, document, page, and crop IDs for auditability.
- Add OCR only as a supplemental signal; do not replace visual page retrieval with OCR chunks.
- Redact secrets from logs and disable verbose request logging in production.
- Add evaluation sets containing tables, crossed wires, symbols, and multi-page references.

## Evaluation ideas

A useful evaluation set should include questions whose answer depends on the page layout rather than a paragraph. Examples include:

- Which terminal is physically connected to the emergency-stop loop?
- Which alarm row corresponds to the pressure switch shown beside the fan starter?
- What is the relationship between the revision cloud and the changed wire number?
- Which motor protection setting appears in the table column for the 7.5 kW drive?
- Which page continues the wire leaving the right edge of the schematic?

Measure page recall at K, crop recall, citation accuracy, answer faithfulness, and the rate of unsupported claims. Keep a human review workflow: an engineer should be able to open the exact page and region used for an answer.

## License and data handling

VisioSync is released under the [MIT License](LICENSE). The license permits commercial and non-commercial use, modification, distribution, sublicensing, and private use, provided that the copyright and permission notice remains with copies or substantial portions of the software.

The MIT License applies to the original source code in this repository. It does not change the terms of third-party dependencies, container images, model checkpoints, fonts, hosted APIs, or documents imported into the application. Review the license and usage terms for every model, package, service, and dataset used in a deployment.

The project contains no rights to engineering manuals or other documents uploaded by users. Uploaded documents remain the responsibility of the deploying organization and may be proprietary, confidential, export-controlled, or subject to contractual retention rules. Do not commit real manuals, rendered customer pages, API keys, production database files, or other sensitive material to Git.

Before operating VisioSync with real engineering data, define the required authentication, authorization, encryption, retention, deletion, audit, and incident-response policies for your organization. The reference application provides an implementation foundation, not legal advice or a complete compliance program.
