from utils.exceptions import ApplicationException, EvaluationException, InvalidDocumentException
from config.config import PDF, MARKDOWN, DOCX, TEXT, MAX_FILE_SIZE
from pathlib import Path
import logging

applogger = logging.getLogger(__name__)

def check_file_validity(file_path: str) -> bool:
    """
    Description: This function validates the input file.
    Assumptions: 
        file already exists, code will not create it. 
        Can process only pdfs, docs, txt and md files.max size 10mb
        Configs contains DOCX=".docx", PDF=".pdf", TEXT=".txt", MARKDOWN=".md", MAX_FILE_SIZE="10_000_000"
    Input: path of the file
    Output: True or False, if the document can be worked with or not
    Raises: Invalid if file missing, wrong type, too large, or read fails
    """
    applogger.info("Inside check_file_validity function")
    try:
        if file_path is None or len(file_path) == 0:
            applogger.error("file_path is None or empty")
            raise InvalidDocumentException("Unable to read the document, filepath is None or empty")
        
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            applogger.error(f"File does not exist: {file_path}")
            raise InvalidDocumentException(f"File not found: {file_path}")
        
        if file_path_obj.is_dir():
            applogger.error("supplied path is a directory")
            raise InvalidDocumentException("Unable to read the document, filepath is of directory")
        
        if file_path_obj.suffix not in (PDF, MARKDOWN, DOCX, TEXT):
            applogger.error("Supplied file type is not supported")
            raise InvalidDocumentException("Unable to read the document, file type is not supported")
        
        if file_path_obj.stat().st_size > int(MAX_FILE_SIZE):
            applogger.error("Supplied file size is larger than 1MB")
            raise InvalidDocumentException("Unable to read the document, file size exceeds 1MB limit")
        applogger.info(f"File Validation Success {file_path}")
        return True
    except InvalidDocumentException as exception:
        applogger.error("InvalidDocumentException in check_file_validity function")
        raise
    except Exception as exception:
        applogger.error(f"Exception in check_file_validity: {str(exception)}")
        raise ApplicationException(exception, context={"error_type": type(exception).__name__})



def take_document(file_name: str) -> bool:
    """
    Description: User provide the document to the application, Function Validate its file, exists and size and not larger than 5MB
    Input:  takes filename
    Output: pass it to the ingestion pipeline for parsing, chunking and embedding
    """
    applogger.info(f"Inside take_documents, recieved filename: {file_name}")
    try:
        is_file_valid = check_file_validity(file_name)
        if not is_file_valid:
            applogger.error("Document supplied is invalid")
            raise InvalidDocumentException("Document supplied is not acceptable")
    except InvalidDocumentException as exception:
        applogger.error("Document supplied is invalid")
        raise
    except Exception as exception:
        applogger.error("Document supplied is invalid")
        raise ApplicationException(str(exception), context={"status":"Document Ingestion Failed", "Message":"Invalid Document, please check logs"})

    