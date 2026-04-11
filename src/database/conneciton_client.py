"""

"""
from utils.exceptions import DatabaseException
from pgvector.psycopg2 import register_vector
from config.config import DB_NAME, DB_PASSWORD, DB_HOST, DB_USER, DB_PORT
from database.queries import INSERT_DOCUMENT_RECORD, CREATE_STRATEGY_RECORD, SELECT_STRATEGY_ID, INSERT_EMBEDDINGS_IN_BATCH
import psycopg2
from psycopg2.extras import execute_values
import json, uuid
import logging

applogger = logging.getLogger(__name__)

def get_connection():
    """
    Discription: This returns the connecton to a database
    Input: Need database_name, username, password, port, hostname
    Output: gives the established connection back
    Raises: DatabaseException
    """
    try:
        applogger.info("Inside get connection")
        db_details = {
            "database":DB_NAME,
            "user":DB_USER,
            "password":"********",
            "host": DB_HOST,
            "port": int(DB_PORT)
        }
        conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=int(DB_PORT),
        )
        register_vector(conn)
        applogger.info("connection returned - Success from get_connection")
        return conn
    except DatabaseException as exception:
        applogger.error(f"Database exception in get_connection  - {db_details}")
        raise
    except Exception as exception:
        applogger.error(f"Database exception - Exception in get_connection - {db_details}")
        raise DatabaseException(str(exception), context={"status":"FAILED", "ErrorMessage":"Unable to connect to DB", "details: ":db_details})
    


def insert_document_id(doc_id: uuid, file_name: str, total_chunks: int, metadata={}):
    """
    Description: Inserting the document id for the document supplied by the user
    Input:doc_id, file_name, total_chunks, metadata
    Output: None (Passed or Success)
    """
    try:
        applogger.info("Inside insert_document_id ")
        connection = get_connection()
        applogger.info("connection received success")
        with connection as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_DOCUMENT_RECORD, (doc_id, file_name, total_chunks, json.dumps(metadata)))
        conn.commit()
        applogger.info("document_id inserted successfully")
    except DatabaseException as exception:
        applogger.error("Database Exception in insert_document_id")
        raise
    except Exception as exception:
        raise DatabaseException(str(exception), context={"status:":"Failed","Error Message:":type(exception).__name__})



def get_or_create_strategy(strategy_name: str, strategy_config: dict) -> int:
    """
    Description: This function is used to check if we already have 
    the recrod for the chunking stratgy we are using or not. If not, it will create it.
    Input: strategy_name (str), strategy_config (dict)
        sample dict: {
            "method":     "hybrid",
            "max_tokens": CHUNK_MAX_TOKENS,
            "model":      EMBEDDING_MODEL,
            "dimensions": EMBEDDING_DIMENSIONS
        }
    Output: None if success, exception if error
    """
    try:
        applogger.info("inside get_or_create_strategy function ")
        if strategy_name is None or strategy_config is None or len(strategy_name) == 0 or len(strategy_config) == 0:
            applogger.error("Strategy name or configs are not valid")
            raise DatabaseException("Check Strategy Name and Config Passes!")
        connection = get_connection()
        applogger.info("connection received success")
        with connection as conn:
            with conn.cursor() as cur:
                # check if exists
                cur.execute(SELECT_STRATEGY_ID, (strategy_name,))
                row = cur.fetchone()
                if row:
                    applogger.info(f"Using existing strategy — id: {row[0]}, name: {strategy_name}")
                    return row[0]
                # create new
                cur.execute(CREATE_STRATEGY_RECORD, (strategy_name, json.dumps(strategy_config)))
                strategy_id = cur.fetchone()[0]
        conn.commit()
        applogger.info(f"New strategy created — id: {strategy_id}, name: {strategy_name}")
        return strategy_id
    except DatabaseException as exception:
        applogger.error("Exception while checking strategy id for the chunking strategy used")
        raise
    except Exception as exception:
        applogger.error("Unexpected error while checking strategy_id for the chunking being used")
        raise DatabaseException(str(exception), context={"status:":"Failed","Error Message:":type(exception).__name__})



def store_embeddings_in_db_batch(embeddings: dict, doc_id: int, strategy_id: int) :
    """
    Description: Store the chunks in the database
    Input: chunks (dict) with text and respective embeddings
    Output: None
    For reference, input embedding:
    final_embedding = {
                index: {
                    "text":text,
                    "embedding":embedding.values
                }
            }
    """
    try:
        applogger.info("Inside storing embeddings in db")
        if embeddings is None or len(embeddings) == 0:
            applogger.error("Received no embeddings, please check")

        connection = get_connection()
        applogger.info("Conenction received success")
        rows = [
            (doc_id, strategy_id, chunk_index, chunk_data["text"], chunk_data["embedding"], json.dumps({"token_count": len(chunk_data["text"].split())})) 
            for chunk_index, chunk_data in embeddings.items()]
        with connection as conn:
            with conn.cursor() as cursor:
                execute_values(cursor, INSERT_EMBEDDINGS_IN_BATCH,rows)
        conn.commit()
        applogger.info(f"Batch insert complete. Rows inserted: {len(rows)}")
    except DatabaseException as exception:
        applogger.error("Exception while storing embeddings into db")
        raise
    except Exception as exception:
        applogger.error("Unexpected error while storing embeddings into db")
        raise DatabaseException(str(exception), context={"status:":"Failed","Error Message:":type(exception).__name__})
