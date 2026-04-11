from dotenv import load_dotenv
import os

load_dotenv()


GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

LLM_MODEL_NAME=os.getenv("LLM_MODEL_NAME")

EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL_NAME")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", 1536))


# --- PostgreSQL ---
PG_HOST=os.getenv("PG_HOST")
PG_PORT=os.getenv("PG_PORT")
PG_DATABASE=os.getenv("PG_DATABASE")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")

LOG_DIR = os.getenv("LOG_DIR", "logs")


PDF=".pdf"
MARKDOWN=".md"
DOCX=".docx" 
TEXT=".txt"
MAX_FILE_SIZE="1_000_000"

