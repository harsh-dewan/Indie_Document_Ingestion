"""
Description: Setting up Embedding Model
Author: Harsh
Version: 0.1.0
"""
from utils.logging import applogger
from utils.exceptions import EmbeddingException, ApplicationException
from config.config import GEMINI_API_KEY, EMBEDDING_DIMENSIONS, EMBEDDING_MODEL
import sys
from google import genai
from google.genai import types



class EmbeddingModel():

    def __init__(self):
        pass    

    def get_model_client(self):
        """
        Description: getting embedding client
        Input: None
        Output: embedding client
        Assumptons: None
        """
        applogger.info("Inside get_embedding_client, Initializing embedding client...")
        try:
            gemini_client = genai.Client()
            applogger.info("Embedding client ready.")
            return gemini_client
        except EmbeddingException as exception:
            applogger.error("Exception while getting embedding_client")
            raise EmbeddingException(str(exception), sys, 
                                {"Status":"Failed", 
                                "Message":"Unable to obtain embedding client"}
                                )
        except Exception as exception:
            applogger.error(f"Exception occured while getting embedding client {str(exception)}")
            raise ApplicationException(str(exception), sys, 
                                    {"Status":"App Failure -- No Embedding Client object created, Error!!", 
                                    "Type":type(exception).__name__}
                                )


    def get_embeddings(self, query: str) -> list[float]:
        """
        Description: This function is used to get the embedding of the content passed
        Input: Content for which embeddings need to be generated
        Output: 1536 dimensional vector
        """
        applogger.info("Inside get_embeddings")
        try:
            embedding_client = self.get_model_client()
            embeddings = embedding_client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=query,
                config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS)
            )
            applogger.info(f"Embedding Generation Success {embeddings}")
            return embeddings
        except EmbeddingException as exception:
            applogger.error("Exception while generating embeddings")
            raise EmbeddingException(str(exception), sys, 
                                {"Status":"Failed", 
                                "Message":"Unable to obtain embeddings from the model"}
                                )
        except Exception as exception:
            applogger.error(f"Exception occured while generating embeddings {str(exception)}")
            raise ApplicationException(str(exception), sys, 
                                    {"Status":"App Failure -- No Embedding generated, Error!!", 
                                    "Type":type(exception).__name__}
                                )


embedding_model=EmbeddingModel()
