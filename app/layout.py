"""
Description: Top-level layout — composes sidebar and chat panel.
             This is the only file that knows both components exist.
Author:      Harsh Dewan
Created:     2026-04-12
Version:     0.1.0
"""

import logging

from sidebar import render_sidebar
from chat import render_chat

applogger = logging.getLogger(__name__)


def render_layout() -> None:
    """
    Description: Renders the full page layout.
                 Sidebar handles upload + ingestion.
                 Main area handles chat.
    Input:  None
    Output: None
    """
    applogger.info("Rendering layout")
    render_sidebar()
    render_chat()
