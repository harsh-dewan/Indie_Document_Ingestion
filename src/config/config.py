"""
Description: Configurations for the project
Author: @harshdewan
Date: 11-04-2026
"""

from dotenv import load_dotenv
import os


load_dotenv()


GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

LLM_MODEL_NAME=os.getenv("LLM_MODEL_NAME")

EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL_NAME")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", 1536))


# --- PostgreSQL ---
DB_HOST=os.getenv("PG_HOST")
DB_PORT=os.getenv("PG_PORT")
DB_NAME=os.getenv("PG_DATABASE")
DB_USER=os.getenv("PG_USER")
DB_PASSWORD=os.getenv("PG_PASSWORD")

LOG_DIR = os.getenv("LOG_DIR", "logs")


PDF=".pdf"
MARKDOWN=".md"
DOCX=".docx" 
TEXT=".txt"
MAX_FILE_SIZE="1_000_000"
CHUNK_MAX_TOKENS=int(os.getenv("CHUNK_MAX_TOKENS", 500))


STRATEGY_NAME="Hybrid_500"
STRATEGY_CONFIG  = {
    "method":     "hybrid",
    "max_tokens": CHUNK_MAX_TOKENS,
    "model":      EMBEDDING_MODEL,
    "dimensions": EMBEDDING_DIMENSIONS
}