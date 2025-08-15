import os
from openai import OpenAI
from younews_reporter.utils import setup_logger
import logging
from dotenv import load_dotenv



class AgenticBase:
    def __init__(self, model: str, logger: logging.Logger = None):
        self.model = model
        try:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception:
            load_dotenv('../.env')
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            raise e

        if logger is None:
            self.logger = setup_logger(__name__)
        else:
            self.logger = logger

    def run(self):
        raise NotImplementedError("Subclasses must implement this method")