# src/ai_models/ollama_model.py
import logging
from typing import List, Dict
import requests
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ai_models.base import AIBaseModel

class OllamaModel(AIBaseModel):
    """
    Concrete implementation of AIBaseModel for Ollama (or compatible local LLM APIs like Oobabooga).
    Assumes a local API endpoint is running.
    """
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = self.config.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.preferred_model = self.config.get("OLLAMA_PREFERRED_MODEL", "llama2")
        self.timeout_seconds = self.config.get("COMPANY_RESEARCH_TIMEOUT_SECONDS", 60)

        if not self.base_url:
            self.logger.error("Ollama Base URL not found in configuration. Ollama models cannot be used.")
            raise ValueError("Ollama Base URL is missing.")

        self.logger.info(f"OllamaModel initialized with base URL: {self.base_url}")

    def _make_api_request(self, endpoint: str, method: str = "GET", json_data: Dict = None, timeout: int = 10) -> Dict:
        """Helper method to make API requests to the Ollama/local LLM server."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=json_data, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Ollama API Connection Error: Could not connect to {url}. Is the Ollama server running? {e}")
            raise ConnectionError(f"Failed to connect to Ollama server at {self.base_url}. Please ensure it's running.") from e
        except requests.exceptions.Timeout:
            self.logger.error(f"Ollama API Request Timeout: Request to {url} timed out after {timeout} seconds.")
            raise TimeoutError(f"Ollama API request timed out for {url}.")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ollama API Request Error: {e}")
            raise RuntimeError(f"Ollama API request failed: {e}") from e
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response from Ollama API: {e}. Raw content: {response.text[:500] if response else 'N/A'}")
            raise ValueError(f"Invalid JSON response from Ollama API: {e}") from e


    def list_available_models(self) -> List[str]:
        self.logger.info("Attempting to list available Ollama models...")
        available_model_names = []
        try:
            data = self._make_api_request("/api/tags", timeout=self.timeout_seconds)
            if "models" in data:
                for model_info in data["models"]:
                    if "name" in model_info:
                        available_model_names.append(model_info["name"].split(":")[0])
            self.logger.info(f"Found {len(available_model_names)} Ollama models.")
        except Exception as e:
            self.logger.error(f"An error occurred while listing Ollama models: {e}")
        return sorted(list(set(available_model_names)))

    def extract_company_info(self, company_name: str, model_name: str, user_template: str, system_message: str) -> Dict:
        """
        Extracts company and subsidiary information using the specified Ollama model.
        This uses the provided prompt template and relies on the AI's internal knowledge.

        Args:
            company_name (str): The name of the company to research.
            model_name (str): The specific Ollama model to use.
            user_template (str): The user prompt template string to use for the AI call.
            system_message (str): The system message string to use for the AI call.

        Returns:
            Dict: A dictionary containing the extracted information.
        """
        self.logger.info(f"Extracting info for '{company_name}' using Ollama model '{model_name}'...")
        
        user_prompt_content = user_template.replace("[COMPANY_PLACEHOLDER]", company_name)

        try:
            json_data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt_content}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 1500
                }
            }
            response_data = self._make_api_request("/api/chat", method="POST", json_data=json_data, timeout=self.timeout_seconds)
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
        return self.preferred_model

if __name__ == "__main__":
    from src.config_loader import load_config
    from src.logger import setup_logging
    from dotenv import load_dotenv
    import os

    test_logger = setup_logging(log_level="DEBUG")
    load_dotenv()

    config = load_config()
    if not config.get("OLLAMA_BASE_URL"):
        test_logger.error("OLLAMA_BASE_URL not set in .env. Cannot run OllamaModel test.")
    else:
        try:
            ollama_instance = OllamaModel(config)
            test_logger.info("OllamaModel instance created successfully.")

            models = ollama_instance.list_available_models()
            test_logger.info(f"Available Ollama models: {models[:5]}...")

            preferred = ollama_instance.get_preferred_model()
            test_logger.info(f"Preferred Ollama model: {preferred}")

            test_company = "Microsoft"
            model_to_use = preferred if preferred in models else "llama2"
            if model_to_use not in models:
                test_logger.warning(f"Preferred model '{preferred}' not found. 'llama2' also not found. Cannot test extraction.")
            else:
                test_prompt_data = config["PROMPT_TEMPLATES"].get(
                    config["DEFAULT_PROMPT_VERSION"], {}
                )
                test_user_template = test_prompt_data.get("user_template", "Default user template for [COMPANY_PLACEHOLDER]")
                test_system_message = test_prompt_data.get("system_message", "Default system message.")

                if test_user_template == "Default user template for [COMPANY_PLACEHOLDER]":
                    test_logger.warning("Using a generic fallback user template for testing.")
                if test_system_message == "Default system message.":
                    test_logger.warning("Using a generic fallback system message for testing.")

                extracted_data = ollama_instance.extract_company_info(test_company, model_to_use, test_user_template, test_system_message)
                test_logger.info(f"Extracted data for {test_company}: {extracted_data}")
                if "error" in extracted_data:
                    test_logger.error(f"Extraction failed: {extracted_data['error']}")

        except ValueError as e:
            test_logger.error(f"Failed to initialize OllamaModel: {e}")
        except ConnectionError as e:
            test_logger.error(f"Ollama server connection error: {e}")
        except Exception as e:
            test_logger.error(f"An unexpected error occurred during OllamaModel test: {e}")
