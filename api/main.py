import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

os.environ["TQDM_DISABLE"] = "1"

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import shutil
import logging

from utils.logging import setup_logging
from utils.exceptions import IngestionException, RetrievalException, InvalidDocumentException
from utils.utils import take_document
from ingestion.ingestion_pipeline import ingestion
from retrieval.retrieval_pipeline import retrieval

setup_logging()
applogger = logging.getLogger(__name__)


app = FastAPI(title="Document Ingestion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    doc_id: str
    strategy_name: str
    top_k: int = 5


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        take_document(tmp_path)
        doc_id, strategy_name = ingestion(tmp_path)
        applogger.info(f"Ingestion success: doc_id={doc_id}")
        return {
            "doc_id": doc_id,
            "strategy_name": strategy_name,
            "filename": file.filename,
        }
    except InvalidDocumentException as e:
        applogger.error(f"Invalid document: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except IngestionException as e:
        applogger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        applogger.error(f"Unexpected error during ingestion: {e}")
        raise HTTPException(status_code=500, detail="Ingestion failed")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = retrieval(
            request.query,
            doc_id=request.doc_id,
            strategy_name=request.strategy_name,
            top_k=request.top_k,
        )
        applogger.info(f"Chat success for doc_id={request.doc_id}")
        return {"response": response}
    except RetrievalException as e:
        applogger.error(f"Retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        applogger.error(f"Unexpected error during retrieval: {e}")
        raise HTTPException(status_code=500, detail="Retrieval failed")
