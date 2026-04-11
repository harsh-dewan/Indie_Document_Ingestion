from utils.logging import applogger
from utils.exceptions import ApplicationException
from embedding.vembedding import vembedding
from chunking.hybrid_chunker import chunker
from models.llm_model import model
from models.embedding_model import embedding_model
from utils.utils import take_document
from ingestion.ingestion_pipeline import ingestion
from retrieval.retrieval_pipeline import retrieval
def main():
    applogger.info("This logger is working from main")
    vembedding()
    chunker()
    llm_response = model.get_llm_response("Give me 10 unique words")
    applogger.info(f"LLM Response: {llm_response}")
    embedding_model.get_embeddings("Hello")
    user_input = input("Please enter the path of the file you wantme to ingest: ")
    safe_user_input = user_input.strip()
    take_document(safe_user_input)
    applogger.info("File path is correct and workable")
    applogger.info("Heading to Ingestion Pipeline")
    ingestion(safe_user_input)
    applogger.info("Ingestion Phase Successfully passed, Heading to Retrieval Phase")
    applogger.info("Asking user to input his query")
    user_input = input("Hi, Any Question? Please:  ")
    safe_user_input = user_input.strip()
    retrieval(safe_user_input)
    applogger.info("Retrieval Phase done, Exiting for now, bye")
    return

if __name__ == "__main__":
    try:
        main()
    except ApplicationException as exception:
        applogger.critical("Application Failure - Please Check")
        applogger.critical(exception)