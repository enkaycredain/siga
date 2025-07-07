# src/config_loader.py
import os
from dotenv import load_dotenv
import logging
import json # Added import for JSON parsing

logger = logging.getLogger('siya_agent')

def load_config():
    """Loads environment variables from .env file and returns a dictionary of configurations."""
    load_dotenv()

    config = {
        # AI Provider API Keys
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),

        # AI Provider Base URLs / Endpoints
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),

        # Preferred/Default Models (will be highlighted in dynamic list)
        "OPENAI_PREFERRED_MODEL": os.getenv("OPENAI_PREFERRED_MODEL", "gpt-4o"),
        "GOOGLE_PREFERRED_MODEL": os.getenv("GOOGLE_PREFERRED_MODEL", "gemini-pro"),
        "OLLAMA_PREFERRED_MODEL": os.getenv("OLLAMA_PREFERRED_MODEL", "llama2"),

        # General Application Settings
        "COMPANY_RESEARCH_TIMEOUT_SECONDS": int(os.getenv("COMPANY_RESEARCH_TIMEOUT_SECONDS", "60")),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO").upper(),
        
        # Prompt Configuration
        "DEFAULT_PROMPT_VERSION": os.getenv("DEFAULT_PROMPT_VERSION", "subsidiary_research_v1") # New default prompt setting
    }

    # Load prompt templates from config/prompts.json
    prompts_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'prompts.json')
    config["PROMPT_TEMPLATES"] = {}
    if os.path.exists(prompts_file_path):
        try:
            with open(prompts_file_path, 'r', encoding='utf-8') as f:
                config["PROMPT_TEMPLATES"] = json.load(f)
            logger.info(f"Loaded {len(config['PROMPT_TEMPLATES'])} prompt templates from {prompts_file_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing prompts.json: {e}. Please check the JSON format.")
            config["PROMPT_TEMPLATES"] = {} # Ensure it's an empty dict on error
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading prompts.json: {e}")
            config["PROMPT_TEMPLATES"] = {}
    else:
        logger.warning(f"prompts.json not found at {prompts_file_path}. No custom prompt templates loaded.")


    # Basic validation (can be expanded later)
    if not config["OPENAI_API_KEY"]:
        logger.warning("OPENAI_API_KEY not found in .env. OpenAI models will not be available.")
    if not config["GOOGLE_API_KEY"]:
        logger.warning("GOOGLE_API_KEY not found in .env. Google AI models will not be available.")

    return config

if __name__ == "__main__":
    from logger import setup_logging
    setup_logging(log_level="DEBUG")

    print("Loading configuration...")
    app_config = load_config()
    print(f"Loaded config: {app_config}")
    print(f"OpenAI API Key: {app_config.get('OPENAI_API_KEY', 'Not Set')}")
    print(f"Company Research Timeout: {app_config.get('COMPANY_RESEARCH_TIMEOUT_SECONDS')} seconds")
    print(f"Loaded Prompt Templates: {list(app_config.get('PROMPT_TEMPLATES', {}).keys())}")
    print(f"Default Prompt Version: {app_config.get('DEFAULT_PROMPT_VERSION')}")

    # Test retrieving a specific prompt
    test_prompt_version = app_config.get("DEFAULT_PROMPT_VERSION")
    if test_prompt_version in app_config["PROMPT_TEMPLATES"]:
        prompt_data = app_config["PROMPT_TEMPLATES"][test_prompt_version]
        print(f"\nDetails for '{test_prompt_version}':")
        print(f"  Description: {prompt_data.get('description')}")
        print(f"  System Message (first 50 chars): {prompt_data.get('system_message', '')[:50]}...")
        print(f"  User Template (first 50 chars): {prompt_data.get('user_template', '')[:50]}...")
    else:
        print(f"Default prompt version '{test_prompt_version}' not found in loaded templates.")
