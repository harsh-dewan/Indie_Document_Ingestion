"""
Description: Setting up Large Language Model
Author: Harsh
Version: 0.1.0
"""
from utils.logging import applogger
from utils.exceptions import ModelException, ApplicationException
from config.config import GEMINI_API_KEY, LLM_MODEL_NAME
import sys
from google import genai


class Model():
    
    def __init__(self):
        self.model_name=LLM_MODEL_NAME
        self.context = ""

    def get_model_client(self):
        """
        Description: Instantiates Gemini Client
        Input: None
        Output: gemini_client
        Assumptions: GEMINI_API_KEY env variable is set
        """
        applogger.info("Inside get_model_client function")
        try:
            gemini_client = genai.Client()       
            applogger.info("Model instantiation success")
            return gemini_client
        except ModelException as exception:
            applogger.error("   ModelClass: ModelException")
            raise ModelException(str(exception), sys, 
                                {"Status":"Failed", 
                                "Message":"LLM Model cannot be instantiated"}
                                )
        except Exception as exception:
            applogger.error("   ModelClass: ApplicationException")
            raise ApplicationException(str(exception), sys, 
                                    {"Status":"App Failure, LLM Client not instantiated", 
                                    "Type":type(exception).__name__}
                                )
        

    def get_llm_response(self, context: str) -> str:
        """
        Description: Function to get llm model response
        Assumptions: None
        Input: Prompt with enough context
        Output: llm response - str type
        """
        applogger.info("Inside get_llm_response")
        if context is None or len(context) == 0:
            applogger.error("   LLM is passed with no context or question, empty string is returned")
            return ""
        try:
            gemini_client = self.get_model_client()
            prompt = f"You are helpful agent, help user with this query {context}."
            response = gemini_client.models.generate_content(model=LLM_MODEL_NAME, contents=prompt)
            applogger.info(f"Response from LLM is success {response.text}")
            return response.text
        except ModelException as exception:
            applogger.error("   ModelClass: ModelException")
            raise ModelException(str(exception), sys, 
                                {"Status":"Failed", 
                                "Message":"Unable to obtain llm response"}
                                )
        except Exception as exception:
            applogger.error("   ModelClass: ApplicationException")
            raise ApplicationException(str(exception), sys, 
                                    {"Status":"App Failure -- No reply from LLM", 
                                    "Type":type(exception).__name__}
                                )
        

model = Model()