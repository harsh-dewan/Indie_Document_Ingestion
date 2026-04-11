import logging
from datetime import datetime
from config.config import LOG_DIR

def setup_logging():
    """
    Configure root logger once at startup.
    """
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
    )

    datetime_now = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    log_file_name = f"{LOG_DIR}/{datetime_now}.log"

    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)
    # console_handler.setFormatter(formatter)

    # attach to ROOT logger — every child logger inherits this
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if not root_logger.hasHandlers():
        root_logger.addHandler(file_handler)
        #root_logger.addHandler(console_handler)

    # docling
    docling_logger = logging.getLogger("docling")
    docling_logger.setLevel(logging.INFO)
    docling_logger.propagate = False
    docling_logger.addHandler(file_handler)

    rapidocr_logger = logging.getLogger("RapidOCR")
    rapidocr_logger.setLevel(logging.INFO)
    rapidocr_logger.addHandler(file_handler)