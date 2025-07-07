# src/ai_models/openai_model.py
import logging
from typing import List, Dict
import openai
from openai import OpenAI
from src.ai_models.base import AIBaseModel # Import the abstract base class

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

    def extract_company_info(self, company_name: str, model_name: str) -> Dict:
        """
        Extracts company and subsidiary information using the specified OpenAI model.
        This uses a basic prompt and relies on the AI's internal knowledge.

        Args:
            company_name (str): The name of the company to research.
            model_name (str): The specific OpenAI model to use.

        Returns:
            Dict: A dictionary containing the extracted information.
        """
        self.logger.info(f"Extracting info for '{company_name}' using OpenAI model '{model_name}'...")
        prompt = (
            f"Based on your internal knowledge, provide the following information for {company_name}:\n"
            f"1. A list of its major direct and indirect subsidiaries globally, including their primary location (city, country).\n"
            f"2. Key financial information (e.g., latest reported annual revenue, net income, market capitalization) with an 'as of' date for each financial figure.\n"
            f"3. Any significant recent news or developments (last 1-2 years) related to its subsidiaries or major operations, with a brief summary and date.\n"
            f"Format the output as a JSON object with the following structure:\n"
            f'{{"company_name": "{company_name}", "extracted_as_of_date": "YYYY-MM-DD (AI knowledge cutoff or current date)",\n'
            f'"subsidiaries": [{{"name": "Subsidiary Name", "location": "City, Country"}}],\n'
            f'"financial_info": [{{"metric": "Revenue", "value": "X billion USD", "as_of_date": "YYYY-MM-DD"}}],\n'
            f'"news_info": [{{"headline": "News Headline", "date": "YYYY-MM-DD", "summary": "Brief summary"}}]}}.\n'
            f"Ensure all information is strictly from your training data and do not perform any external searches."
        )

        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a highly knowledgeable and precise corporate research assistant. Provide information strictly from your training data and do not hallucinate or perform external searches. Focus on factual, verifiable data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1, # Keep temperature low to reduce hallucination
                max_tokens=1500, # Adjust as needed for comprehensive output
                response_format={"type": "json_object"} # Request JSON output
            )
            raw_content = response.choices[0].message.content
            self.logger.debug(f"OpenAI raw response: {raw_content}")
            # Attempt to parse the JSON string
            import json
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
    # You would typically run this from src/main.py.
    from src.config_loader import load_config
    from src.logger import setup_logging
    import os

    # Set up basic logging for standalone test
    test_logger = setup_logging(log_level="DEBUG")

    # Ensure .env is loaded for the test
    # This is important for standalone testing if API keys are only in .env
    from dotenv import load_dotenv
    load_dotenv()

    config = load_config()
    if not config.get("OPENAI_API_KEY"):
        test_logger.error("OPENAI_API_KEY not set in .env. Cannot run OpenAIModel test.")
    else:
        try:
            openai_instance = OpenAIModel(config)
            test_logger.info("OpenAIModel instance created successfully.")

            # Test list_available_models
            models = openai_instance.list_available_models()
            test_logger.info(f"Available OpenAI models: {models[:5]}...") # Print first 5 models

            # Test get_preferred_model
            preferred = openai_instance.get_preferred_model()
            test_logger.info(f"Preferred OpenAI model: {preferred}")

            # Test extract_company_info (using a test company)
            test_company = "Coca-Cola"
            # Ensure the preferred model is in the available list, or pick a common one like 'gpt-3.5-turbo'
            # For actual usage, you'd select from the 'models' list
            model_to_use = preferred if preferred in models else "gpt-3.5-turbo"
            if model_to_use not in models:
                test_logger.warning(f"Preferred model '{preferred}' not found. 'gpt-3.5-turbo' also not found. Cannot test extraction.")
            else:
                extracted_data = openai_instance.extract_company_info(test_company, model_to_use)
                test_logger.info(f"Extracted data for {test_company}: {extracted_data}")
                if "error" in extracted_data:
                    test_logger.error(f"Extraction failed: {extracted_data['error']}")

        except ValueError as e:
            test_logger.error(f"Failed to initialize OpenAIModel: {e}")
        except Exception as e:
            test_logger.error(f"An unexpected error occurred during OpenAIModel test: {e}")
