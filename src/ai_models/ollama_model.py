# src/ai_models/ollama_model.py
import logging
from typing import List, Dict
import requests
import json
import sys # Import sys
import os  # Import os

# Add the project root directory (siya/) to the Python path
# This allows importing modules like src.ai_models.base when this file is run directly for testing.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ai_models.base import AIBaseModel # Import the abstract base class

class OllamaModel(AIBaseModel):
    """
    Concrete implementation of AIBaseModel for Ollama (or compatible local LLM APIs like Oobabooga).
    Assumes a local API endpoint is running.
    """
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = self.config.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.preferred_model = self.config.get("OLLAMA_PREFERRED_MODEL", "llama2") # Default if not in config

        if not self.base_url:
            self.logger.error("Ollama Base URL not found in configuration. Ollama models cannot be used.")
            raise ValueError("Ollama Base URL is missing.")

        self.logger.info(f"OllamaModel initialized with base URL: {self.base_url}")

    def _make_api_request(self, endpoint: str, method: str = "GET", json_data: Dict = None) -> Dict:
        """Helper method to make API requests to the Ollama/local LLM server."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=10) # 10 second timeout for listing models
            elif method == "POST":
                response = requests.post(url, json=json_data, timeout=self.config.get("COMPANY_RESEARCH_TIMEOUT_SECONDS", 60))
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Ollama API Connection Error: Could not connect to {url}. Is the Ollama server running? {e}")
            raise ConnectionError(f"Failed to connect to Ollama server at {self.base_url}. Please ensure it's running.") from e
        except requests.exceptions.Timeout:
            self.logger.error(f"Ollama API Request Timeout: Request to {url} timed out.")
            raise TimeoutError(f"Ollama API request timed out for {url}.")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ollama API Request Error: {e}")
            raise RuntimeError(f"Ollama API request failed: {e}") from e
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response from Ollama API: {e}. Raw content: {response.text[:500] if response else 'N/A'}")
            raise ValueError(f"Invalid JSON response from Ollama API: {e}") from e


    def list_available_models(self) -> List[str]:
        """
        Lists available Ollama models by querying the local Ollama API.

        Returns:
            List[str]: A list of available Ollama model names.
        """
        self.logger.info("Attempting to list available Ollama models...")
        available_model_names = []
        try:
            # Ollama's list models endpoint
            data = self._make_api_request("/api/tags")
            if "models" in data:
                for model_info in data["models"]:
                    if "name" in model_info:
                        available_model_names.append(model_info["name"].split(":")[0]) # Get base name, e.g., "llama2" from "llama2:latest"
            self.logger.info(f"Found {len(available_model_names)} Ollama models.")
        except Exception as e:
            self.logger.error(f"An error occurred while listing Ollama models: {e}")
        return sorted(list(set(available_model_names))) # Return unique and sorted list

    def extract_company_info(self, company_name: str, model_name: str) -> Dict:
        """
        Extracts company and subsidiary information using the specified Ollama model.
        This uses a basic prompt and relies on the AI's internal knowledge.

        Args:
            company_name (str): The name of the company to research.
            model_name (str): The specific Ollama model to use.

        Returns:
            Dict: A dictionary containing the extracted information.
        """
        self.logger.info(f"Extracting info for '{company_name}' using Ollama model '{model_name}'...")
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
            # Ollama chat completions endpoint
            # Note: Ollama's API might vary slightly if using Oobabooga's text-generation-webui
            # This example uses Ollama's /api/chat endpoint for consistency with OpenAI/Gemini message format
            json_data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a highly knowledgeable and precise corporate research assistant. Provide information strictly from your training data and do not hallucinate or perform external searches. Focus on factual, verifiable data. Respond only with the requested JSON object."},
                    {"role": "user", "content": prompt}
                ],
                "stream": False, # We want a single response, not a stream
                "options": {
                    "temperature": 0.1, # Keep temperature low
                    "num_predict": 1500 # Max tokens equivalent
                }
            }
            response_data = self._make_api_request("/api/chat", method="POST", json_data=json_data)
            raw_content = response_data.get("message", {}).get("content", "")
            self.logger.debug(f"Ollama raw response: {raw_content}")

            extracted_data = json.loads(raw_content)
            self.logger.info(f"Successfully extracted info for '{company_name}' using Ollama.")
            return extracted_data
        except (ConnectionError, TimeoutError, RuntimeError) as e:
            self.logger.error(f"Ollama API communication error for {company_name} with model {model_name}: {e}")
            return {"error": f"Ollama API communication error: {e}"}
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response from Ollama for {company_name}: {e}. Raw content: {raw_content[:500]}...")
            return {"error": f"JSON parsing error: {e}"}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during Ollama extraction for {company_name}: {e}")
            return {"error": f"Unexpected error: {e}"}

    def get_preferred_model(self) -> str:
        """
        Returns the preferred/default Ollama model name from configuration.
        """
        return self.preferred_model

if __name__ == "__main__":
    # This block is for testing the OllamaModel directly.
    from src.config_loader import load_config
    from src.logger import setup_logging
    from dotenv import load_dotenv
    import os

    test_logger = setup_logging(log_level="DEBUG")
    load_dotenv() # Ensure .env is loaded for the test

    config = load_config()
    if not config.get("OLLAMA_BASE_URL"):
        test_logger.error("OLLAMA_BASE_URL not set in .env. Cannot run OllamaModel test.")
    else:
        try:
            ollama_instance = OllamaModel(config)
            test_logger.info("OllamaModel instance created successfully.")

            # Test list_available_models
            models = ollama_instance.list_available_models()
            test_logger.info(f"Available Ollama models: {models[:5]}...") # Print first 5 models

            # Test get_preferred_model
            preferred = ollama_instance.get_preferred_model()
            test_logger.info(f"Preferred Ollama model: {preferred}")

            # Test extract_company_info (using a test company)
            test_company = "Microsoft"
            # Ensure the preferred model is in the available list, or pick a common one like 'llama2'
            model_to_use = preferred if preferred in models else "llama2" # Fallback to llama2 if preferred not found
            if model_to_use not in models:
                test_logger.warning(f"Preferred model '{preferred}' not found. 'llama2' also not found. Cannot test extraction.")
            else:
                test_logger.info(f"Attempting extraction for {test_company} using model {model_to_use}...")
                extracted_data = ollama_instance.extract_company_info(test_company, model_to_use)
                test_logger.info(f"Extracted data for {test_company}: {extracted_data}")
                if "error" in extracted_data:
                    test_logger.error(f"Extraction failed: {extracted_data['error']}")

        except ValueError as e:
            test_logger.error(f"Failed to initialize OllamaModel: {e}")
        except ConnectionError as e:
            test_logger.error(f"Ollama server connection error: {e}")
        except Exception as e:
            test_logger.error(f"An unexpected error occurred during OllamaModel test: {e}")
