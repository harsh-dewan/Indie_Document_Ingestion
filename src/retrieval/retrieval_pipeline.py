from utils.exceptions import RetrievalException
import logging
applogger = logging.getLogger(__name__)


def retrieval(user_query: str):
    applogger.info(f"Inside retrieval function with query: {user_query}")
    pass