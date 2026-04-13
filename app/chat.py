"""
Description: Chat panel component — renders conversation history and handles
             user queries by calling your existing retrieval() pipeline.
Author:      Harsh Dewan
Created:     2026-04-12
Version:     0.1.0
"""

import logging
import streamlit as st

from retrieval.retrieval_pipeline import retrieval
from utils.exceptions import RetrievalException, DatabaseException, EmbeddingException
from state import (
    CHAT_HISTORY,
    DOC_ID,
    INGESTION_DONE,
    STRATEGY_NAME,
)

applogger = logging.getLogger(__name__)

TOP_K = 5

ROLE_USER      = "user"
ROLE_ASSISTANT = "assistant"


def render_chat() -> None:
    """
    Description: Main chat panel. Renders message history then the input box.
                 Only active once a document has been ingested.
    Input:  None — reads from session state
    Output: None
    """
    if not st.session_state.get(INGESTION_DONE):
        _render_empty_state()
        return

    _render_history()
    _render_input()


def _render_empty_state() -> None:
    """
    Description: Placeholder shown before a document is ingested.
    Input:  None
    Output: None
    """
    st.markdown("## 💬 Chat with your Document")
    st.info("Upload and ingest a document from the sidebar to start chatting.")


def _render_history() -> None:
    """
    Description: Renders all previous messages in the conversation.
    Input:  None — reads CHAT_HISTORY from session state
    Output: None
    """
    st.markdown("## 💬 Chat with your Document")

    history = st.session_state.get(CHAT_HISTORY, [])

    if not history:
        st.caption("Ask anything about your document.")
        return

    for message in history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _render_input() -> None:
    """
    Description: Renders the chat input box and triggers retrieval on submit.
    Input:  None
    Output: None
    """
    user_query = st.chat_input("Ask a question about your document...")

    if not user_query or not user_query.strip():
        return

    user_query = user_query.strip()
    applogger.info("User query received: %s", user_query)

    _append_message(ROLE_USER, user_query)

    with st.chat_message(ROLE_USER):
        st.markdown(user_query)

    _handle_query(user_query)


def _handle_query(user_query: str) -> None:
    """
    Description: Calls your retrieval() pipeline and renders the response.
                 Appends both the query and response to chat history.
    Input:  user_query — cleaned string from the chat input
    Output: None — updates CHAT_HISTORY in session state
    """
    try:
        with st.chat_message(ROLE_ASSISTANT):
            with st.spinner("Retrieving from document..."):
                llm_response = retrieval(
                    user_query,
                    doc_id=st.session_state[DOC_ID],
                    strategy_name=st.session_state[STRATEGY_NAME],
                    top_k=TOP_K,
                )

            if not llm_response:
                llm_response = "Sorry, I could not find relevant content in the document for your query."

            st.markdown(llm_response)
            applogger.info("Response rendered for query: %s", user_query)

        _append_message(ROLE_ASSISTANT, llm_response)

    except (RetrievalException, EmbeddingException, DatabaseException) as exception:
        applogger.error("Retrieval failed for query '%s': %s", user_query, str(exception))
        _render_error(f"Retrieval failed — {type(exception).__name__}. Check logs for details.")

    except Exception as exception:
        applogger.error("Unexpected error during retrieval: %s", str(exception))
        _render_error("Something went wrong. Please try again.")


def _append_message(role: str, content: str) -> None:
    """
    Description: Appends a single message dict to the chat history in session state.
    Input:  role    — "user" or "assistant"
            content — message text
    Output: None
    """
    st.session_state[CHAT_HISTORY].append({"role": role, "content": content})


def _render_error(message: str) -> None:
    """
    Description: Shows an error inside the assistant chat bubble and
                 records it in history so the conversation stays intact.
    Input:  message — user-facing error string
    Output: None
    """
    with st.chat_message(ROLE_ASSISTANT):
        st.error(message)
    _append_message(ROLE_ASSISTANT, f"⚠️ {message}")
