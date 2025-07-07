# src/ai_models/google_ai_model.py
import logging
from typing import List, Dict
import google.generativeai as genai
import json
from src.ai_models.base import AIBaseModel # Import the abstract base class

class GoogleAIModel(AIBaseModel):
    """
    Concrete implementation of AIBaseModel for Google AI (Gemini) models.
    """
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = self.config.get("GOOGLE_API_KEY")
        self.preferred_model = self.config.get("GOOGLE_PREFERRED_MODEL", "gemini-pro") # Default if not in config

        if not self.api_key:
            self.logger.error("Google AI API key not found in configuration. Google AI models cannot be used.")
            raise ValueError("Google AI API key is missing.")

        genai.configure(api_key=self.api_key)
        self.logger.info("GoogleAIModel initialized.")

    def list_available_models(self) -> List[str]:
        """
        Lists available Google AI models that are typically used for text generation.

        Returns:
            List[str]: A list of available Google AI model IDs.
        """
        self.logger.info("Attempting to list available Google AI models...")
        available_model_ids = []
        try:
            for m in genai.list_models():
                # Filter for models capable of generating text
                # and commonly used for chat/completion tasks.
                # This heuristic might need adjustment over time.
                if 'generateContent' in m.supported_generation_methods and \
                   ("gemini" in m.name or "text-bison" in m.name):
                    available_model_ids.append(m.name)
            self.logger.info(f"Found {len(available_model_ids)} Google AI models.")
        except Exception as e:
            self.logger.error(f"An error occurred while listing Google AI models: {e}")
            if "API key not valid" in str(e):
                self.logger.error("Google AI Authentication Error: Invalid API Key. Cannot list models.")
        return sorted(list(set(available_model_ids))) # Return unique and sorted list

    def extract_company_info(self, company_name: str, model_name: str) -> Dict:
        """
        Extracts company and subsidiary information using the specified Google AI model.
        This uses a basic prompt and relies on the AI's internal knowledge.

        Args:
            company_name (str): The name of the company to research.
            model_name (str): The specific Google AI model to use.

        Returns:
            Dict: A dictionary containing the extracted information.
        """
        self.logger.info(f"Extracting info for '{company_name}' using Google AI model '{model_name}'...")
        try:
            model = genai.GenerativeModel(model_name)
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

            # For Gemini, we typically use generate_content
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1, # Keep temperature low
                    candidate_count=1,
                    response_mime_type="application/json" # Request JSON output
                )
            )
            # Access the text from the response
            raw_content = response.text
            self.logger.debug(f"Google AI raw response: {raw_content}")

            # Attempt to parse the JSON string
            extracted_data = json.loads(raw_content)
            self.logger.info(f"Successfully extracted info for '{company_name}' using Google AI.")
            return extracted_data
        except ValueError as e: # Catch errors from genai.GenerativeModel (e.g., model not found)
            self.logger.error(f"Google AI Model Error for {company_name} with model {model_name}: {e}")
            return {"error": f"Google AI Model error: {e}"}
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response from Google AI for {company_name}: {e}. Raw content: {raw_content[:500]}...")
            return {"error": f"JSON parsing error: {e}"}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during Google AI extraction for {company_name}: {e}")
            return {"error": f"Unexpected error: {e}"}

    def get_preferred_model(self) -> str:
        """
        Returns the preferred/default Google AI model name from configuration.
        """
        return self.preferred_model

if __name__ == "__main__":
    # This block is for testing the GoogleAIModel directly.
    from src.config_loader import load_config
    from src.logger import setup_logging
    from dotenv import load_dotenv
    import os

    test_logger = setup_logging(log_level="DEBUG")
    load_dotenv() # Ensure .env is loaded for the test

    config = load_config()
    if not config.get("GOOGLE_API_KEY"):
        test_logger.error("GOOGLE_API_KEY not set in .env. Cannot run GoogleAIModel test.")
    else:
        try:
            google_ai_instance = GoogleAIModel(config)
            test_logger.info("GoogleAIModel instance created successfully.")

            # Test list_available_models
            models = google_ai_instance.list_available_models()
            test_logger.info(f"Available Google AI models: {models[:5]}...") # Print first 5 models

            # Test get_preferred_model
            preferred = google_ai_instance.get_preferred_model()
            test_logger.info(f"Preferred Google AI model: {preferred}")

            # Test extract_company_info (using a test company)
            test_company = "PepsiCo"
            model_to_use = preferred if preferred in models else "gemini-pro"
            if model_to_use not in models:
                test_logger.warning(f"Preferred model '{preferred}' not found. 'gemini-pro' also not found. Cannot test extraction.")
            else:
                extracted_data = google_ai_instance.extract_company_info(test_company, model_to_use)
                test_logger.info(f"Extracted data for {test_company}: {extracted_data}")
                if "error" in extracted_data:
                    test_logger.error(f"Extraction failed: {extracted_data['error']}")

        except ValueError as e:
            test_logger.error(f"Failed to initialize GoogleAIModel: {e}")
        except Exception as e:
            test_logger.error(f"An unexpected error occurred during GoogleAIModel test: {e}")
