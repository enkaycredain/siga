# src/ai_models/openai_model.py
import logging
from typing import List, Dict
import openai
from openai import OpenAI
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ai_models.base import AIBaseModel

class OpenAIModel(AIBaseModel):
    """
    Concrete implementation of AIBaseModel for OpenAI GPT models.
    """
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = self.config.get("OPENAI_API_KEY")
        self.preferred_model = self.config.get("OPENAI_PREFERRED_MODEL", "gpt-4o") # Default if not in config

        if not self.api_key:
            self.logger.error("OpenAI API key not found in configuration. OpenAI models cannot be used.")
            raise ValueError("OpenAI API key is missing.")

        self.client = OpenAI(api_key=self.api_key)
        self.logger.info("OpenAIModel initialized.")

    def list_available_models(self) -> List[str]:
        """
        Lists available OpenAI models that are typically used for chat completions.
        Filters for models that are generally suitable for text generation.

        Returns:
            List[str]: A list of available OpenAI model IDs.
        """
        self.logger.info("Attempting to list available OpenAI models...")
        available_model_ids = []
        try:
            # Fetch all models and filter for chat-capable ones
            # This list might need to be updated as OpenAI changes its models
            response = self.client.models.list()
            for model in response.data:
                # Filter for common chat/completion models.
                # This is a heuristic and might need adjustment.
                if "gpt" in model.id or "davinci" in model.id or "babbage" in model.id or "curie" in model.id or "ada" in model.id:
                    available_model_ids.append(model.id)
            self.logger.info(f"Found {len(available_model_ids)} OpenAI models.")
        except openai.AuthenticationError:
            self.logger.error("OpenAI Authentication Error: Invalid API Key. Cannot list models.")
        except openai.APIConnectionError as e:
            self.logger.error(f"OpenAI API Connection Error: Could not connect to OpenAI API. {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while listing OpenAI models: {e}")
        return sorted(list(set(available_model_ids))) # Return unique and sorted list

    def extract_company_info(self, company_name: str, model_name: str, user_template: str, system_message: str) -> Dict: # Updated signature
        """
        Extracts company and subsidiary information using the specified OpenAI model.
        This uses the provided prompt template and relies on the AI's internal knowledge.

        Args:
            company_name (str): The name of the company to research.
            model_name (str): The specific OpenAI model to use.
            user_template (str): The user prompt template string to use for the AI call.
            system_message (str): The system message string to use for the AI call.

        Returns:
            Dict: A dictionary containing the extracted information.
        """
        self.logger.info(f"Extracting info for '{company_name}' using OpenAI model '{model_name}'...")
        
        # Replace the placeholder in the user_template with the actual company name
        user_prompt_content = user_template.replace("[COMPANY_PLACEHOLDER]", company_name)

        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_message}, # Use the passed system_message
                    {"role": "user", "content": user_prompt_content} # Use the prepared user_prompt_content
                ],
                temperature=0.1, # Keep temperature low to reduce hallucination
                max_tokens=1500, # Adjust as needed for comprehensive output
                response_format={"type": "json_object"} # Request JSON output
            )
            raw_content = response.choices[0].message.content
            self.logger.debug(f"OpenAI raw response: {raw_content}")
            # Attempt to parse the JSON string
            extracted_data = json.loads(raw_content)
            self.logger.info(f"Successfully extracted info for '{company_name}' using OpenAI.")
            return extracted_data
        except openai.APIStatusError as e:
            self.logger.error(f"OpenAI API error for {company_name} with model {model_name}: Status {e.status_code}, Message: {e.response.json()}")
            return {"error": f"OpenAI API error: {e.status_code} - {e.response.json().get('message', 'Unknown API error')}"}
        except openai.APIConnectionError as e:
            self.logger.error(f"OpenAI API connection error for {company_name}: {e}")
            return {"error": f"OpenAI API connection error: {e}"}
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response from OpenAI for {company_name}: {e}. Raw content: {raw_content[:500]}...")
            return {"error": f"JSON parsing error: {e}"}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during OpenAI extraction for {company_name}: {e}")
            return {"error": f"Unexpected error: {e}"}

    def get_preferred_model(self) -> str:
        """
        Returns the preferred/default OpenAI model name from configuration.
        """
        return self.preferred_model

if __name__ == "__main__":
    # This block is for testing the OpenAIModel directly.
    from src.config_loader import load_config
    from src.logger import setup_logging
    from dotenv import load_dotenv
    import os

    test_logger = setup_logging(log_level="DEBUG")
    load_dotenv()

    config = load_config()
    if not config.get("OPENAI_API_KEY"):
        test_logger.error("OPENAI_API_KEY not set in .env. Cannot run OpenAIModel test.")
    else:
        try:
            openai_instance = OpenAIModel(config)
            test_logger.info("OpenAIModel instance created successfully.")

            models = openai_instance.list_available_models()
            test_logger.info(f"Available OpenAI models: {models[:5]}...")

            preferred = openai_instance.get_preferred_model()
            test_logger.info(f"Preferred OpenAI model: {preferred}")

            test_company = "Coca-Cola"
            model_to_use = preferred if preferred in models else "gpt-3.5-turbo"
            if model_to_use not in models:
                test_logger.warning(f"Preferred model '{preferred}' not found. 'gpt-3.5-turbo' also not found. Cannot test extraction.")
            else:
                # Use prompt data from config for testing
                test_prompt_data = config["PROMPT_TEMPLATES"].get(
                    config["DEFAULT_PROMPT_VERSION"], {}
                )
                test_user_template = test_prompt_data.get("user_template", "Default user template for [COMPANY_PLACEHOLDER]")
                test_system_message = test_prompt_data.get("system_message", "Default system message.")

                if test_user_template == "Default user template for [COMPANY_PLACEHOLDER]":
                    test_logger.warning("Using a generic fallback user template for testing.")
                if test_system_message == "Default system message.":
                    test_logger.warning("Using a generic fallback system message for testing.")

                extracted_data = openai_instance.extract_company_info(test_company, model_to_use, test_user_template, test_system_message)
                test_logger.info(f"Extracted data for {test_company}: {extracted_data}")
                if "error" in extracted_data:
                    test_logger.error(f"Extraction failed: {extracted_data['error']}")

        except ValueError as e:
            test_logger.error(f"Failed to initialize OpenAIModel: {e}")
        except Exception as e:
            test_logger.error(f"An unexpected error occurred during OpenAIModel test: {e}")
