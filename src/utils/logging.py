import logging
from datetime import datetime
from config.config import LOG_DIR


def logger_configuration():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    datetime_now = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    log_file_name = f"{LOG_DIR}/{datetime_now}.log"
    filehandler = logging.FileHandler(log_file_name)
    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(filehandler)

    return logger



applogger=logger_configuration()