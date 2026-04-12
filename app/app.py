"""
Description: Entry point for the Streamlit frontend
Author:      Harsh Dewan
Created:     2026-04-12
Version:     0.1.0
"""

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from utils.logging import setup_logging
from layout import render_layout


setup_logging()


st.set_page_config(
    page_title="Indie Document Ingestor",
    layout="wide",
    initial_sidebar_state="expanded",
)


render_layout()
