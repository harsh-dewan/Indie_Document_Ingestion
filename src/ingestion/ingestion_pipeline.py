"""
Description: This is the Ingestion pipeline of the project
Aim is to take the file_path from the user and store it in vector database for later retrieval
Author:  @harshdewan
Date: 11-04-2026

"""

from pathlib import Path

from utils.exceptions import IngestionException, EmbeddingException, DatabaseException
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.chunking import HybridChunker
from config.config import CHUNK_MAX_TOKENS, STRATEGY_NAME, STRATEGY_CONFIG
from database.conneciton_client import insert_document_id, get_or_create_strategy, store_embeddings_in_db_batch
from models.embedding_model import embedding_model
from pathlib import Path
import uuid
import json
import logging

applogger = logging.getLogger(__name__)


def get_pdf_parsed(filename: str):
    """
    Description: This function uses docling library to parse pdf
    Input: vetted file name
    Output: parsed pdf object of type ConversionResult
    """
    applogger.info(f"Parsing PDF: %s", {filename})
    pipeline_options = PdfPipelineOptions()
    pipeline_options.generate_picture_images = True
    pipeline_options.generate_table_images = True
    try:
        if not filename or filename is None:
            raise IngestionException("Parsing Exception, invalid filename")
        converter = DocumentConverter(
                            format_options={
                                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                            }
                    )
        result = converter.convert(str(filename))
        """
        Following code is for debugging only, will be removed or commented in actual
        """
        output_path = Path("outputs/parsed_document.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        applogger.info(f"Writing docling object to output.json at path: {output_path}")
        with open(output_path, "w") as file:
            json.dump(result.document.export_to_dict(), file, indent=2)
        # output_path.write_text(
        #     json.dumps(result.document.export_to_dict(), indent=2),
        #     encoding="utf-8",
        # )
        applogger.info(f"Parsed document written to {output_path}")
        applogger.info("Document Parsing SUCCESS!!")
        return result
    except IngestionException as exception:
        applogger.error("Ingestion Exception Occurred")
        raise
    except Exception as exception:
        applogger.error("Exception Occurred")
        raise IngestionException(str(exception), context={"status":"Failed to parse pdf, check logs", "ErrorMessage":type(exception).__name__})


def get_chunks(parsed_document, max_tokens: int = CHUNK_MAX_TOKENS) -> list:
    """
    Description:  This function takes on parsed document object of type ConversionResult and chunks into smaller chunks
    Input: parsed_document_object, max_token per chunk
    Output: list of chunks
    """
    applogger.info("Inside get_chunks function")
    try:
        if parsed_document is None:
            applogger.info("parsed_document is None")
            raise IngestionException("parsed_document is None")
        if max_tokens < 1:
            applogger.info("Max_Tokens must be a positive integer")
            raise IngestionException("Max_Tokens must be a positive integer")
        chunker = HybridChunker(max_tokens=max_tokens)
        chunks = list(chunker.chunk(parsed_document.document))
        applogger.info(f"Created {len(chunks)} chunks with max tokens {max_tokens}")
        return chunks
    except IngestionException as exception:
        applogger.error("Ingestion Exception in get_chunk_method, please check")
        raise
    except Exception as exception:
        applogger.error("Exception in get_chunk_method, please check")
        raise IngestionException(str(exception), context={"status":"Failed in pahse 2 chunking", "ErrorMessage":type(exception).__name__})
    

def normalise_chunks(chunks):
    pass

def get_embeddings(finalised_chunks):
    """
    Description: This is used to get the embeddding using embedding model
    Input: Chunks of the document parsed
    Output: Dictionary containing the text and the respective embeddings
    """
    try:
        applogger.info("Inside the get_embeddings function")
        if finalised_chunks is None or len(finalised_chunks) == 0:
            raise IngestionException("Chunks passed are empty")
        final_embedding = {}
        all_texts = [chunk.text for chunk in finalised_chunks]
        all_embeddings = embedding_model.get_embeddings(all_texts)
        final_embedding = {
            index: {
                "text":text,
                "embedding":embedding.values
            }
            for index,(text,embedding) in enumerate(zip(all_texts, all_embeddings.embeddings))
        }
        embedding_file = Path("outputs/embedding.json")
        embedding_file.parent.mkdir(parents=True, exist_ok=True)
        with open(embedding_file, "w") as file:
            json.dump(final_embedding, file, indent=2)
        applogger.info("Embeddings successfully generted")
        return final_embedding
    except IngestionException as exception:
        applogger.error("Ingestion Exception -- Error while generating embeddings")
        raise
    except EmbeddingException as exception:
        applogger.error("Embedding Exception -- Error while generating embeddings")
        raise 
    except Exception as exception:
        applogger.error("Ingestion Exception -- Error while generating embeddings")
        raise IngestionException(str(exception), context={"status":"Failed", "ErrorMessage":"Failure while generating embeddings"})




def store_embeddings(embedding: dict, file_name:str, total_chunks: int, metadata={}):
    """
    Description: This is used to store the embedding in PgVector
    Input: Dictionary containing the text and its respective embeddings
    Output: Success or Failure
    #This need to be split into separate function 
    """
    applogger.info("Inside Storing Embeddings in DB")
    try:
        if embedding is None or len(embedding) == 0:
            raise IngestionException("No embeddings passed")
        doc_id = str(uuid.uuid4())

        """
        Get Document Id
        """
        insert_document_id(doc_id=doc_id, file_name=file_name, total_chunks=total_chunks, metadata=metadata)
        applogger.info("Document inserted — id: %s, file: %s", doc_id, file_name)

        """
        Get Chunking Strategy Id
        """
        strategy_id = get_or_create_strategy(STRATEGY_NAME, STRATEGY_CONFIG)
        applogger.info(f"Created or Got Strategy Id: {strategy_id}")

        """
        Storing in DB
        """
        store_embeddings_in_db_batch(embedding, doc_id, strategy_id)
        applogger.info("All Embeddings addedd successfully")
        applogger.info(f"=== Ingest pipeline complete — {doc_id} ===")
        return doc_id, strategy_id
    
    except IngestionException:
        applogger.error("Ingestion Exception: Error while storing the embeddings")
        raise

    except DatabaseException as exception:
        applogger.error("Ingestion Exception: Error from database connection and storing embeddings")
        raise

    except Exception as exception:
        applogger.error("Unexpected Exception Occured in Ingestion Phase")
        raise IngestionException(str(exception), context={"status":"failed", "Message: ":type(exception).__name__})

def ingestion(file_name):
    """
    Description: This will
    1. Parse the pdf with docling library
    2. make chunks of the parsed data
    3. Handle Text, Table and Image
    4. Embed date into vectors 
    5. Store the embedding into PGVector

    Input: Takes the file_name 
    Output: Embedding Vectors    
    """
    try:
        if file_name is None or len(file_name) == 0:
            applogger.error("IngestionException: Invalid filename")
            raise IngestionException("Invalid Filename")

        #Phase 1 -- Parsing the document
        pdf_parsed = get_pdf_parsed(file_name)
        applogger.info("===== Pdf Parsed Successfully ======")

        #Phase 2 -- Chunk the parsed document from phase 1
        chunks = get_chunks(pdf_parsed)
        applogger.info("===== Chunking Done Successfully =====")

        #Phase 3 -- Text, Table and Image
        #finalised_chunks = normalise_chunks(chunks)

        #Phase 4 -- Embed the chunks
        embeddings = get_embeddings(chunks)
        applogger.info("===== Embeddings Generated Successfully =====")

        #Phase 5 -- Store in PgVector
        (doc_id, strategy_id) = store_embeddings(embeddings, file_name=file_name, total_chunks=len(chunks), metadata={})
        applogger.info("===== Embedding Stored Successfully =====")
        
        applogger.info("===== Ingestion Pipeline Successfully Executed =====")
        applogger.info(f"document_id: {doc_id} and strategy_id: {strategy_id}")
        return (doc_id, strategy_id)
    
    except IngestionException as exception:
        applogger.error("Ingestion Pipeline failed!!, please check logs")
        raise
    except DatabaseException as exception:
        applogger.error("Ingestion Exception: Error from database connection and storing embeddings")
        raise
    except EmbeddingException as exception:
        applogger.error("Embedding Exception -- Error while generating embeddings")
        raise 