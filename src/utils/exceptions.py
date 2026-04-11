"""
Description: Exception Definitions to be used across the application
Author:      Harsh Dewan
Created:     2026-04-10
Version:     0.1.0
"""


"""
A better approach is to raise exceptions that 
already contain the information needed to diagnose the problem:
    what failed,
    where it failed,
    why it failed,
    what the original traceback was.
"""
import sys
import traceback
import logging

applogger = logging.getLogger(__name__)

class ApplicationException(Exception):

    def __init__(self, err_message: str, err_details=sys, context: dict =  None):
        super().__init__(str(err_message))
        _, _, exec_trb = err_details.exc_info()
        self.error_message = str(err_message)
        self.context = context or  {}

        if exec_trb is not None:
            self.file_name = exec_trb.tb_frame.f_code.co_filename
            self.line_number = exec_trb.tb_lineno
        else:
            self.file_name = "Unknown"
            self.line_number = -1

        self.traceback_str = ''.join(traceback.format_exception(*err_details.exc_info()))

    def __str__(self):
        return (
            f"\n\nError in [{self.file_name}] at line [{self.line_number}] \n"
            f"Message: {self.error_message} \n"
            f"Traceback: {self.traceback_str} \n"
            f"Context: {self.context} \n\n"
        )



class ModelException(ApplicationException):
    pass


class EmbeddingException(ApplicationException):
    pass


class EvaluationException(ApplicationException):
    pass


class IngestionException(ApplicationException):
    pass


class PromptException(ApplicationException):
    pass


class RetrievalException(ApplicationException):
    pass


class InvalidDocumentException(ApplicationException):
    pass


class DatabaseException(ApplicationException):
    pass



