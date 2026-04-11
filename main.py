from utils.logging import applogger
from utils.exceptions import ApplicationException
from embedding.vembedding import vembedding
from chunking.hybrid_chunker import chunker
from models.llm_model import get_model

def main():
    applogger.info("This logger is working from main")
    vembedding()
    chunker()
    get_model()
    return

if __name__ == "__main__":
    try:
        main()
    except ApplicationException as exception:
        applogger.critical("Main--Exception Occured, Please Check")
        applogger.critical(exception)