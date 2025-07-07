# src/ai_models/google_ai_model.py
import logging
from typing import List, Dict
import google.generativeai as genai
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ai_models.base import AIBaseModel

class GoogleAIModel(AIBaseModel):
    """
    Concrete implementation of AIBaseModel for Google AI (Gemini) models.
    """
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = self.config.get("GOOGLE_API_KEY")
        self.preferred_model = self.config.get("GOOGLE_PREFERRED_MODEL", "gemini-pro")
        self.timeout_seconds = self.config.get("COMPANY_RESEARCH_TIMEOUT_SECONDS", 60)

        if not self.api_key:
            self.logger.error("Google AI API key not found in configuration. Google AI models cannot be used.")
            raise ValueError("Google AI API key is missing.")

        genai.configure(api_key=self.api_key)
        self.logger.info("GoogleAIModel initialized.")

    def list_available_models(self) -> List[str]:
        self.logger.info("Attempting to list available Google AI models...")
        available_model_ids = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods and \
                   ("gemini" in m.name or "text-bison" in m.name):
                    available_model_ids.append(m.name)
            self.logger.info(f"Found {len(available_model_ids)} Google AI models.")
        except Exception as e:
            self.logger.error(f"An error occurred while listing Google AI models: {e}")
            if "API key not valid" in str(e):
                self.logger.error("Google AI Authentication Error: Invalid API Key. Cannot list models.")
            elif "timed out" in str(e).lower() or "deadline exceeded" in str(e).lower():
                self.logger.error(f"Google AI API Timeout Error: Request to list models timed out after {self.timeout_seconds} seconds. {e}")
            else:
                self.logger.error(f"An unexpected error occurred while listing Google AI models: {e}")
        return sorted(list(set(available_model_ids)))

    def extract_company_info(self, company_name: str, model_name: str, user_template: str, system_message: str) -> Dict:
        """
        Extracts company and subsidiary information using the specified Google AI model.
        This uses the provided prompt template and relies on the AI's internal knowledge.

        Args:
            company_name (str): The name of the company to research.
            model_name (str): The specific Google AI model to use.
            user_template (str): The user prompt template string to use for the AI call.
            system_message (str): The system message string to use for the AI call.

        Returns:
            Dict: A dictionary containing the extracted information.
        """
        self.logger.info(f"Extracting info for '{company_name}' using Google AI model '{model_name}'...")
        try:
            model = genai.GenerativeModel(model_name)
            
            user_prompt_content = user_template.replace("[COMPANY_PLACEHOLDER]", company_name)

            response = model.generate_content(
                user_prompt_content,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    candidate_count=1,
                    response_mime_type="application/json"
                ),
                request_options={"timeout": self.timeout_seconds}
            )
            raw_content = response.text
            self.logger.debug(f"Google AI raw response: {raw_content}")
            extracted_data = json.loads(raw_content)
            self.logger.info(f"Successfully extracted info for '{company_name}' using Google AI.")
            return extracted_data
        except ValueError as e:
            self.logger.error(f"Google AI Model Error for {company_name} with model {model_name}: {e}")
            return {"error": f"Google AI Model error: {e}"}
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response from Google AI for {company_name}: {e}. Raw content: {raw_content[:500]}...")
            return {"error": f"JSON parsing error: {e}"}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during Google AI extraction for {company_name}: {e}")
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
    if not config.get("GOOGLE_API_KEY"):
        test_logger.error("GOOGLE_API_KEY not set in .env. Cannot run GoogleAIModel test.")
    else:
        try:
            google_ai_instance = GoogleAIModel(config)
            test_logger.info("GoogleAIModel instance created successfully.")

            models = google_ai_instance.list_available_models()
            test_logger.info(f"Available Google AI models: {models[:5]}...")

            preferred = google_ai_instance.get_preferred_model()
            test_logger.info(f"Preferred Google AI model: {preferred}")

            test_company = "PepsiCo"
            model_to_use = preferred if preferred in models else "gemini-pro"
            if model_to_use not in models:
                test_logger.warning(f"Preferred model '{preferred}' not found. 'gemini-pro' also not found. Cannot test extraction.")
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

                extracted_data = google_ai_instance.extract_company_info(test_company, model_to_use, test_user_template, test_system_message)
                test_logger.info(f"Extracted data for {test_company}: {extracted_data}")
                if "error" in extracted_data:
                    test_logger.error(f"Extraction failed: {extracted_data['error']}")

        except ValueError as e:
            test_logger.error(f"Failed to initialize GoogleAIModel: {e}")
        except Exception as e:
            test_logger.error(f"An unexpected error occurred during GoogleAIModel test: {e}")
