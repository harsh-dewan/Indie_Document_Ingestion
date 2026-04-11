from utils.logging import applogger
from utils.exceptions import ApplicationException
from embedding.vembedding import vembedding
from chunking.hybrid_chunker import chunker
from models.llm_model import model
from models.embedding_model import embedding_model
from utils.utils import take_document

def main():
    applogger.info("This logger is working from main")
    vembedding()
    chunker()
    llm_response = model.get_llm_response("Give me 10 unique words")
    applogger.info(f"LLM Response: {llm_response}")
    embedding_model.get_embeddings("Hello")
    user_input = input("Please enter the path of the file you wantme to ingest: ")
    take_document(user_input)
    applogger.info("File path is correct and workable")
    applogger.info("Heading to Ingestion Pipeline")
    return

if __name__ == "__main__":
    try:
        main()
    except ApplicationException as exception:
        applogger.critical("Application Failure - Please Check")
        applogger.critical(exception)