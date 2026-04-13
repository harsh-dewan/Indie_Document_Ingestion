"""
Description: Sidebar component — handles file upload and ingestion pipeline trigger.
             Calls ingestion() from your existing pipeline directly.
             No logic lives here beyond UI concerns.
Author:      Harsh Dewan
Created:     2026-04-12
Version:     0.1.0
"""

import tempfile
import os
import logging
import streamlit as st

from ingestion.ingestion_pipeline import ingestion
from utils.exceptions import IngestionException, EmbeddingException, DatabaseException
from ingestion.ingestion_pipeline import get_pdf_parsed, get_chunks, get_embeddings, store_embeddings
from state import (
    init_session_state,
    reset_session_state,
    DOC_ID,
    STRATEGY_NAME,
    INGESTION_DONE,
    TOTAL_CHUNKS,
    UPLOADED_FILE,
)

applogger = logging.getLogger(__name__)

SUPPORTED_TYPES = ["pdf", "txt", "md", "docx"]


def _save_upload_to_temp(uploaded_file) -> str:
    """
    Description: Streamlit gives us bytes in memory, not a file path.
                 Your ingestion pipeline expects a file path.
                 This saves the upload to a named temp file and returns its path.
    Input:  uploaded_file — st.UploadedFile object
    Output: str — absolute path to the saved temp file
    """
    suffix = os.path.splitext(uploaded_file.name)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        applogger.info("Uploaded file saved to temp path: %s", tmp.name)
        return tmp.name


def _run_ingestion(file_path: str) -> tuple[str, str, int]:
    """
    Description: Thin wrapper around your ingestion() pipeline.
                 Separates the pipeline call from all UI concerns.
    Input:  file_path — path to the saved temp file
    Output: (doc_id, strategy_name, chunk_count)
    Raises: IngestionException, EmbeddingException, DatabaseException
    """
    applogger.info("Triggering ingestion pipeline for: %s", file_path)
    (doc_id, strategy_name) = ingestion(file_path)
    applogger.info("Ingestion complete — doc_id: %s, strategy: %s", doc_id, strategy_name)
    return doc_id, strategy_name


def render_sidebar() -> None:
    """
    Description: Renders the sidebar.
                 Upload → Ingest button → pipeline status → result summary.
    Input:  None
    Output: None — writes to st.session_state on success
    """
    init_session_state()

    with st.sidebar:
        st.title("📄 Indie Document Ingestor")
        st.caption("Upload a document to begin")

        st.divider()

        uploaded_file = st.file_uploader(
            label="Choose a document",
            type=SUPPORTED_TYPES,
            help="Supported: PDF, TXT, Markdown, DOCX — max 10 MB",
        )

        if uploaded_file is None:
            st.info("No document uploaded yet.")
            return

        # New file uploaded — reset previous session
        if uploaded_file.name != st.session_state[UPLOADED_FILE]:
            applogger.info("New file detected — resetting session")
            reset_session_state()
            init_session_state()
            st.session_state[UPLOADED_FILE] = uploaded_file.name

        st.success(f"**{uploaded_file.name}** selected")

        if st.session_state[INGESTION_DONE]:
            _render_ingestion_summary()
            return

        if st.button("Ingest Document", type="primary", use_container_width=True):
            _handle_ingestion(uploaded_file)


def _handle_ingestion(uploaded_file) -> None:
    temp_path = None
    try:
        with st.status("Running ingestion pipeline...", expanded=True) as status:

            st.write("💾 Saving upload...")
            temp_path = _save_upload_to_temp(uploaded_file)
            st.write("✅ File saved")

            st.write("📑 Parsing document with Docling — this takes 20-40 seconds...")
            pdf_parsed = get_pdf_parsed(temp_path)
            st.write(f"✅ Document parsed")

            st.write("✂️  Chunking...")
            chunks = get_chunks(pdf_parsed)
            st.write(f"✅ {len(chunks)} chunks created")

            st.write("🔢 Generating embeddings via Gemini...")
            embeddings = get_embeddings(chunks)
            st.write(f"✅ Embeddings generated")

            st.write("🗄️  Storing in PgVector...")
            (doc_id, strategy_name) = store_embeddings(
                embeddings,
                file_name=temp_path,
                total_chunks=len(chunks),
                metadata={}
            )
            st.write("✅ Stored in database")

            st.session_state[DOC_ID]         = doc_id
            st.session_state[STRATEGY_NAME]  = strategy_name
            st.session_state[INGESTION_DONE] = True

            status.update(label="Ingestion complete ✅", state="complete", expanded=False)

        _render_ingestion_summary()

    except (IngestionException, EmbeddingException, DatabaseException) as exception:
        applogger.error("Ingestion failed: %s", str(exception))
        st.error(f"Ingestion failed — {type(exception).__name__}. Check logs.")
    except Exception as exception:
        applogger.error("Unexpected error during ingestion: %s", str(exception))
        st.error("Something went wrong. Please try again.")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def _render_ingestion_summary() -> None:
    """
    Description: Shows a compact summary after successful ingestion.
    Input:  None — reads from session state
    Output: None
    """
    st.divider()
    st.markdown("**Document ready**")
    st.markdown(f"- Strategy: `{st.session_state[STRATEGY_NAME]}`")
    st.caption(f"Doc ID: `{st.session_state[DOC_ID]}`")
    st.divider()
    st.caption("Upload a new file to start over.")
