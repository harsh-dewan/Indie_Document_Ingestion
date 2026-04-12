from utils.logging import setup_logging
from utils.exceptions import ApplicationException, ModelException, IngestionException, InvalidDocumentException, EmbeddingException, RetrievalException
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
        llm_response = model.get_llm_response("Give me a unique english word, rarely used")
        applogger.info(f"LLM Response Success: {llm_response}")
        embedding_model.get_embeddings("Hello")

        #Input Document
        user_input = input("Please enter the path of the file you want me to ingest: ")
        safe_user_input = user_input.strip()
        take_document(safe_user_input)
        applogger.info("File path is correct and workable")

        #Ingestion Pipeline
        applogger.info("Heading to Ingestion Pipeline")
        (doc_id, strategy_name) = ingestion(safe_user_input)
        applogger.info("Ingestion Phase Successfully passed, Heading to Retrieval Phase")

        #Retrieval Phase
        applogger.info("Asking user to input his query")
        print("\n\nModel: I am ready to answer your questions, Please tell me")
        while True:
            user_input = input("\n\nUser: ").strip()
            if not user_input:
                applogger.error("Empty query provided.")
                continue
            if user_input.lower() in ("exit", "bye"):
                applogger.info("Bye for now!!")
                break
            llm_response = retrieval(user_input, doc_id=doc_id, strategy_name=strategy_name, top_k=5)
            print("\n\nModel: ", llm_response)
        print("\n\nModel: Thank you for your time, It was my pleasure serving you. Bye for now")
        applogger.info("Thank you, Exiting for now, bye")
            
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
    except RetrievalException as exception:
        applogger.error("Application Failure - Retrieval Phase Failed")
        raise ApplicationException(str(exception), context={"status":"FAILURE", "ErrorMessage":"Failed in Retrieval Document Phase"})
    except Exception as exception:
        applogger.error("Application Failure - Something unexpected happend")
        raise ApplicationException(str(exception), context={"status":"FAILURE", "ErrorMessage":"Project Failure"})



if __name__ == "__main__":
    try:
        main()
    except ApplicationException as exception:
        applogger.critical("Application Failure - Please Check")
        applogger.critical(str(exception))