"""
Description: This is the Ingestion pipeline of the project
Aim is to take the file_path from the user and store it in vector database for later retrieval
Author:  @harshdewan
Date: 11-04-2026

"""

from utils.logging import applogger
from utils.exceptions import ApplicationException, EvaluationException


def get_pdf_parsing(file_name):
    pass

def get_chunks(pdf_parsed):
    pass

def normalise_chunks(chunks):
    pass

def get_embeddings(finalised_chunks):
    pass

def store_embeddings(embedding):
    pass

def ingestion(file_name):
    """
    Description: This will
    1. Parse the pdf with docling library
    2. make chunks of the parsed data
    3. Handle Text, Table and Image
    4. Embed date into vectors into PGVector

    Input: Takes the file_name 
    Output: Embedding Vectors    
    """
    #Phase 1 -- Parsing the document
    pdf_parsed = get_pdf_parsing(file_name)

    #Phase 2 -- Chunk the parsed document from phase 1
    chunks = get_chunks(pdf_parsed)

    #Phase 3 -- Text, Table and Image
    finalised_chunks = normalise_chunks(chunks)

    #Phase 4 -- Embed the chunks
    embeddings = get_embeddings(finalised_chunks)

    #Phase 5 -- Store in PgVector
    store_embeddings(embeddings)
    pass