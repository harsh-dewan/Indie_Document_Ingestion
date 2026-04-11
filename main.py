from utils.logging import setup_logging
from utils.exceptions import ApplicationException, ModelException, IngestionException, InvalidDocumentException, EmbeddingException
from models.llm_model import model
from models.embedding_model import embedding_model
from utils.utils import take_document
from ingestion.ingestion_pipeline import ingestion
from retrieval.retrieval_pipeline import retrieval
import logging, os


os.environ["TQDM_DISABLE"] = "1"

setup_logging()
applogger = logging.getLogger(__name__)


def main():
    try:
        print("\nWelcome the Document Ingestor,Its my pleasure to serve you :)")
        print("\nStarting with Ingestion Phase")

        #Model
        print("\nGetting LLM Model and Embedding Model ready for you")
        applogger.info("Testing with input - ")
        llm_response = model.get_llm_response("Give me 5 unique english words")
        applogger.info(f"LLM Response Success: {llm_response}")
        embedding_model.get_embeddings("Hello")

        #Input Document
        user_input = input("Please enter the path of the file you wantme to ingest: ")
        safe_user_input = user_input.strip()
        take_document(safe_user_input)
        applogger.info("File path is correct and workable")

        #Ingestion Pipeline
        applogger.info("Heading to Ingestion Pipeline")
        ingestion(safe_user_input)
        applogger.info("Ingestion Phase Successfully passed, Heading to Retrieval Phase")

        #Retrieval Phase
        applogger.info("Asking user to input his query")
        user_input = input("Hi, Any Question? Please:  ")
        safe_user_input = user_input.strip()
        retrieval(safe_user_input)
        applogger.info("Retrieval Phase done, Exiting for now, bye")
            
    except InvalidDocumentException as exception:
        applogger.error("Application Failure - Invalid Document")
        raise ApplicationException(str(exception), context={"status":"FAILURE", "ErrorMessage":"Failed to Validate Document"})
    except ModelException as exception:
        applogger.error("Application Failure - Cannot Instantiate LLM Model")
        raise ApplicationException(str(exception), context={"status":"FAILURE", "ErrorMessage":"Failed to Instantiate LLM Model"})
    except EmbeddingException as exception:
        applogger.error("Application Failure - Cannot Instantiate Embedding Model")
        raise ApplicationException(str(exception), context={"status":"FAILURE", "ErrorMessage":"Failed to Instantiate Embedding Model"})
    except IngestionException as exception:
        applogger.error("Application Failure - Ingestion Phase Failed")
        raise ApplicationException(str(exception), context={"status":"FAILURE", "ErrorMessage":"Failed to Ingest Document"})
    except Exception as exception:
        applogger.error("Application Failure - Something unexpected happend")
        raise ApplicationException(str(exception), context={"status":"FAILURE", "ErrorMessage":"Project Failure"})



if __name__ == "__main__":
    try:
        main()
    except ApplicationException as exception:
        applogger.critical("Application Failure - Please Check")
        applogger.critical(str(exception))