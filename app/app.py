"""
Description: Entry point for the Streamlit frontend
Author:      Harsh Dewan
Created:     2026-04-12
Version:     0.1.0
"""

import sys
import os
import streamlit as st
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from utils.logging import setup_logging
from layout import render_layout


setup_logging()
applogger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Indie Document Ingestor",
    layout="wide",
    initial_sidebar_state="expanded",
)


render_layout()


@st.cache_resource
def initialise_models():
    """
    Description: Warms up LLM and embedding model once at startup.
                 Shared across all reruns — not recreated.
    Input:  None
    Output: None
    """
    from models.llm_model import model
    from models.embedding_model import embedding_model
    model.get_llm_response("ping")
    embedding_model.get_embeddings("ping")
    applogger.info("Models warmed up and cached")

initialise_models()