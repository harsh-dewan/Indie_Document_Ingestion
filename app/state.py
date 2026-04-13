"""
Description: Streamlit session state initialisation and helpers
             Centralises all st.session_state keys so no magic strings
             are scattered across the UI modules.
Author:      Harsh Dewan
Created:     2026-04-12
Version:     0.1.0
"""

import logging

applogger = logging.getLogger(__name__)


# ── Key constants ────────────────────────────────────────────────────────────

DOC_ID          = "doc_id"
STRATEGY_NAME   = "strategy_name"
CHAT_HISTORY    = "chat_history"
INGESTION_DONE  = "ingestion_done"
TOTAL_CHUNKS    = "total_chunks"
UPLOADED_FILE   = "uploaded_filename"


def init_session_state() -> None:
    """
    Description: Initialise all session state keys with safe defaults.
                 Call once at the top of every page render — idempotent.
    Input:  None
    Output: None
    """
    applogger.info("Initialising session state")

    defaults = {
        DOC_ID:        None,
        STRATEGY_NAME: None,
        CHAT_HISTORY:  [],
        INGESTION_DONE: False,
        TOTAL_CHUNKS:  0,
        UPLOADED_FILE: None,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_session_state() -> None:
    """
    Description: Wipe all keys — called when user uploads a new document.
    Input:  None
    Output: None
    """
    applogger.info("Resetting session state for new document")

    keys_to_clear = [
        DOC_ID, STRATEGY_NAME, CHAT_HISTORY,
        INGESTION_DONE, TOTAL_CHUNKS, UPLOADED_FILE,
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)


# late import — streamlit must be imported after set_page_config in app.py
import streamlit as st
