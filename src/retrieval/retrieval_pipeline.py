from utils.exceptions import RetrievalException, DatabaseException, EmbeddingException
import logging
from models.embedding_model import embedding_model
from database.conneciton_client import get_contextual_embeddings
from models.llm_model import model
applogger = logging.getLogger(__name__)
import sys


def get_user_input_embeddings(user_query: str) -> list[float]:
    """
    Description: this function generates the embedding of the user_query
    Input: user_input - string type
    Output: list of embedded values - float type
    """
    try:
        applogger.info("Inside get_user_input_embeddings")
        if user_query is None or len(user_query) == 0:
            raise RetrievalException("User input is empty")
        all_embeddings = embedding_model.get_embeddings(user_query)
        applogger.info(f"Embeddings successfully generted for {user_query}")
        applogger.info(f"Embedding generated: {all_embeddings}")
        return all_embeddings
    except RetrievalException as exception:
        applogger.error("Retrieval Exception, error while retrieving context")
        raise
    except EmbeddingException as exception:
        applogger.error("Retrieval Phase Embedding Exception -- Error while generating embeddings ")
        raise 
    except Exception as exception:
        applogger.error("Unexpected error while retrieving context")
        raise RetrievalException(str(exception), sys, context={})
    


def get_context_from_document(doc_id, embeddings: list[float], strategy_name, top_k) -> list[str]:
    """
    Description: this function fetches the related content from DB based on the user_input
    Input: embeddings - list[float]
    Output: list[str] -- actual content from the document which isrelated to user_query
    """
    try:
        applogger.info("Inside get_context_from_document")
        if embeddings is None or len(embeddings) == 0:
            applogger.error("Retrieval exception occur - passed embeddings are empty") 
            raise RetrievalException("Retrieval exception occur - passed embeddings are empty")   
        #make a call in DB to search for similar contextual documents
        similar_context = get_contextual_embeddings(doc_id, embeddings, strategy_name, top_k)
        applogger.info("Contextual daa found from DB, Success")
        return similar_context
    except RetrievalException as exception:
        applogger.error("Retrieval Exception, error while retrieving context", sys, context={})
        raise
    except DatabaseException as exception:
        applogger.error("Retrieval Exception: Error from database connection and searching for related content")
        raise
    except Exception as exception:
        applogger.error("Unexpected error while retrieving context")
        raise RetrievalException(str(exception), sys, context={})


def get_model_response(user_query: str, user_query_context: list[str]) -> str:
    """
    Description: This will give the actual response from the LLM
    Input: user_query, user_query_context (foundin DB)
    Output: LLM Response
    """
    try:
        if user_query is None or user_query_context is None:
            return "No Content found in the document rleated to your query"
        prompt = (
            "You are a helpful assistant who responds to user queries with the "
            "required information based on the question asked and how depth the user wants to cover.\n\n"
            "Keep your answers from the document only. Do not go beyond what is said in the "
            "document or anything extra you are aware of. If the document does not "
            "mention anything, say: Sorry, this information is not present in the document provided.\n\n"
            f"Context:\n{user_query_context}\n\n"
            f"User Query: {user_query}"
        )
        llm_response = model.get_llm_response(prompt)
        applogger.info(f"LLM Response: {llm_response}")
        return llm_response
    except RetrievalException as exception:
        applogger.error("Retrieval Exception, error while retrieving context")
        raise
    except Exception as exception:
        applogger.error("Unexpected error while retrieving context")
        raise RetrievalException(str(exception), sys, context={})


def retrieval(user_query: str, doc_id: str, strategy_name: str, top_k: int) -> str:
    """
    Stages:
    1. Converting userInput into Embeddings
    2. Searching related document content in VectorDB
    3. Passing Context to LLM Model and generate response
    """
    applogger.info(f"Inside retrieval function with query: {user_query}")
    try:
        if user_query is None or len(user_query) == 0:
            raise RetrievalException()
        #Stage 1
        embedddings = get_user_input_embeddings(user_query)
        applogger.info("embedding generation for user query is success")

        #Stage 2
        user_query_context = get_context_from_document(doc_id, embedddings.embeddings[0].values, strategy_name, top_k)
        applogger.info("user query context fetched successfully")

        #Stage 3
        llm_response = get_model_response(user_query, user_query_context)
        applogger.info(f"Generated Response: {llm_response}")
        return llm_response

    except RetrievalException as exception:
        applogger.error("Retrieval Exception, error while retrieving context")
        raise
    except DatabaseException as exception:
        applogger.error("Retrieval Database Exception: Error from database connection and searching embeddings")
        raise
    except EmbeddingException as exception:
        applogger.error("Retrieval Embedding Exception -- Error while generating embeddings")
        raise 