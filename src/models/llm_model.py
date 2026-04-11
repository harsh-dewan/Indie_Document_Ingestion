"""
Description: Setting up Large Language Model
Author: Harsh
Version: 0.1.0
"""
from utils.logging import applogger
from utils.exceptions import ModelException, ApplicationException
import sys


def sample_llm_call():
    pass


def get_model():
    applogger.info("Inside Model Class")
    try:
        applogger.info("Model Generation Done")
    except ModelException as exception:
        applogger.error("ModelClass: ModelException")
        raise ModelException(str(exception), sys, 
                             {"Status":"Failed", 
                              "Message":"LLM Model cannot be instantiate"}
                            )
    except Exception as exception:
        applogger.error("ModelClass: ApplicationException")
        raise ApplicationException(str(exception), sys, 
                                {"Status":"App Failure", 
                                "Type":type(exception).__name__}
                            )