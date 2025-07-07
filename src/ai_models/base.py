# src/ai_models/base.py
from abc import ABC, abstractmethod
from typing import List, Dict
import logging

class AIBaseModel(ABC):
    """
    Abstract Base Class (ABC) for all AI model integrations in SIGA.
    Defines the common interface that all AI providers must implement.
    """

    def __init__(self, config: Dict):
        """
        Initializes the AI model with necessary configuration.
        Subclasses should call super().__init__(config) and then
        initialize their specific client (e.g., OpenAI client, Google AI client).

        Args:
            config (Dict): A dictionary containing application configuration,
                           including API keys and preferred model names.
        """
        self.config = config
        self.logger = logging.getLogger('siga.app')

    @abstractmethod
    def list_available_models(self) -> List[str]:
        """
        Abstract method to dynamically list available models for this AI provider.

        Returns:
            List[str]: A list of strings, where each string is the name of an available model.
        """
        pass

    @abstractmethod
    def extract_company_info(self, company_name: str, model_name: str, user_template: str, system_message: str) -> Dict:
        """
        Abstract method to extract company and subsidiary information using the AI model.
        This method should leverage the AI's internal knowledge only.

        Args:
            company_name (str): The name of the company to research.
            model_name (str): The specific AI model to use for the extraction.
            user_template (str): The user prompt template string to use for the AI call.
            system_message (str): The system message string to use for the AI call.

        Returns:
            Dict: A dictionary containing the extracted information.
                  Expected keys might include:
                  - "company_name": str
                  - "subsidiaries": List[Dict] (each dict having "name", "location", etc.)
                  - "financial_info": Dict (e.g., "revenue": ..., "as_of_date": ...)
                  - "news_info": List[Dict] (each dict having "headline", "date", "summary")
                  - "extracted_as_of_date": str (date reflecting AI's knowledge cut-off or current date)
                  If extraction fails, an empty dictionary or a dictionary with an "error" key can be returned.
        """
        pass

    @abstractmethod
    def get_preferred_model(self) -> str:
        """
        Abstract method to return the preferred/default model name for this AI provider.
        This model will be highlighted in the interactive selection.

        Returns:
            str: The name of the preferred model.
        """
        pass

if __name__ == "__main__":
    print("This is an abstract base class. It cannot be instantiated directly.")
    print("Concrete AI model implementations will inherit from AIBaseModel.")
