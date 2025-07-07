# src/main.py
import argparse
import logging
import sys
import os

# Add the parent directory (siya/) to the Python path
# This allows importing modules within src/ as src.module_name
# This is a common pattern for runnable scripts within a package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_loader import load_config
from src.logger import setup_logging

# Import concrete AI model implementations
from src.ai_models.openai_model import OpenAIModel
# from src.ai_models.google_ai_model import GoogleAIModel # Will uncomment when implemented
# from src.ai_models.ollama_model import OllamaModel     # Will uncomment when implemented

def main():
    """
    Main entry point for the SIYA agent application.
    Handles configuration loading, logging setup, and CLI argument parsing.
    Orchestrates interactive AI provider and model selection.
    """
    # Load configuration first
    config = load_config()

    # Set up logging based on loaded config
    siya_logger = setup_logging(log_level=config.get("LOG_LEVEL", "INFO"))

    siya_logger.info("SIYA Agent started.")
    siya_logger.debug(f"Loaded configuration: {config}")

    parser = argparse.ArgumentParser(
        description="Subsidiary Intelligence Yielding Analyst (SIYA) Agent."
    )
    parser.add_argument(
        "--company",
        type=str,
        help="Name of the single company to research (e.g., 'PepsiCo')."
    )
    parser.add_argument(
        "--csv_file",
        type=str,
        help="Path to a CSV file containing a list of companies."
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "google_ai", "ollama"],
        help="Choose the AI provider to use (openai, google_ai, ollama). Required if not interactive.",
        required=False
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Specific AI model name to use (e.g., 'gpt-4o', 'gemini-pro', 'llama2'). "
             "If not provided in interactive mode, a list of available models will be shown."
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode, prompting for choices."
    )

    args = parser.parse_args()

    # --- Interactive Mode Logic ---
    if args.interactive:
        siya_logger.info("Running in interactive mode.")
        chosen_provider = None

        available_providers = ["openai", "google_ai", "ollama"]
        provider_display_names = {
            "openai": "OpenAI (GPT Models)",
            "google_ai": "Google AI (Gemini Models)",
            "ollama": "Ollama (Local LLMs)"
        }
        preferred_provider = available_providers[0] # Default to 'openai' for highlighting

        siya_logger.info("\n--- Choose an AI Provider ---")
        for i, provider in enumerate(available_providers):
            display_name = provider_display_names.get(provider, provider)
            highlight_marker = " *" if provider == preferred_provider else ""
            print(f"{i+1}. {display_name}{highlight_marker}")

        while chosen_provider not in available_providers:
            try:
                choice_input = input(f"Enter your choice (1-{len(available_providers)}) or press Enter for default ({preferred_provider}): ").strip()
                if not choice_input:
                    chosen_provider = preferred_provider
                    print(f"Using default provider: {chosen_provider}")
                elif choice_input.isdigit() and 1 <= int(choice_input) <= len(available_providers):
                    chosen_provider = available_providers[int(choice_input) - 1]
                else:
                    print("Invalid choice. Please enter a number from the list or press Enter for default.")
            except Exception as e:
                print(f"An error occurred during selection: {e}")
                siya_logger.error(f"Error during provider selection: {e}")
                return # Exit gracefully

        args.provider = chosen_provider
        siya_logger.info(f"Selected AI Provider: {args.provider}")

        # --- Dynamic Model Selection Logic (Task 6 Part 2) ---
        ai_instance = None
        try:
            if args.provider == "openai":
                ai_instance = OpenAIModel(config)
             elif args.provider == "google_ai":
                 ai_instance = GoogleAIModel(config)  
            elif args.provider == "ollama":
                 ai_instance = OllamaModel(config)   
            else:
                siya_logger.error(f"AI provider '{args.provider}' is not yet implemented or recognized.")
                return

            if ai_instance:
                available_models = ai_instance.list_available_models()
                if not available_models:
                    siya_logger.error(f"No models found for {args.provider}. Check API key and connection.")
                    return

                preferred_model = ai_instance.get_preferred_model()
                if preferred_model not in available_models:
                    siya_logger.warning(f"Preferred model '{preferred_model}' not found among available models. Falling back to first available.")
                    preferred_model = available_models[0] # Fallback if preferred isn't available

                siya_logger.info(f"\n--- Choose a Model for {args.provider} ---")
                for i, model in enumerate(available_models):
                    highlight_marker = " *" if model == preferred_model else ""
                    print(f"{i+1}. {model}{highlight_marker}")

                chosen_model = None
                while chosen_model not in available_models:
                    try:
                        model_choice_input = input(f"Enter your choice (1-{len(available_models)}) or press Enter for default ({preferred_model}): ").strip()
                        if not model_choice_input:
                            chosen_model = preferred_model
                            print(f"Using default model: {chosen_model}")
                        elif model_choice_input.isdigit() and 1 <= int(model_choice_input) <= len(available_models):
                            chosen_model = available_models[int(model_choice_input) - 1]
                        else:
                            print("Invalid choice. Please enter a number from the list or press Enter for default.")
                    except Exception as e:
                        print(f"An error occurred during model selection: {e}")
                        siya_logger.error(f"Error during model selection: {e}")
                        return # Exit gracefully

                args.model = chosen_model
                siya_logger.info(f"Selected AI Model: {args.model}")

        except ValueError as e:
            siya_logger.error(f"Configuration error for {args.provider}: {e}")
            return
        except Exception as e:
            siya_logger.error(f"Failed to initialize AI instance for {args.provider}: {e}")
            return

    # --- Non-Interactive Mode Logic ---
    else: # Non-interactive mode
        if not args.provider:
            siya_logger.error("Provider must be specified in non-interactive mode. Exiting.")
            return
        if not args.model:
            siya_logger.error("Model must be specified in non-interactive mode if not interactive. Exiting.")
            return
        siya_logger.info(f"Running non-interactive with Provider: {args.provider}, Model: {args.model}")

        # In non-interactive mode, we still need to instantiate the AI model
        ai_instance = None
        try:
            if args.provider == "openai":
                ai_instance = OpenAIModel(config)
            # elif args.provider == "google_ai":
            #     ai_instance = GoogleAIModel(config) # Uncomment when implemented
            # elif args.provider == "ollama":
            #     ai_instance = OllamaModel(config)   # Uncomment when implemented
            else:
                siya_logger.error(f"AI provider '{args.provider}' is not yet implemented or recognized for non-interactive mode.")
                return
        except ValueError as e:
            siya_logger.error(f"Configuration error for {args.provider} in non-interactive mode: {e}")
            return
        except Exception as e:
            siya_logger.error(f"Failed to initialize AI instance for {args.provider} in non-interactive mode: {e}")
            return

    siya_logger.info("--- End of Task 6 (Part 2) Implementation ---")
    siya_logger.info(f"Next: Complete other AI integrations and core agent orchestration.")

    # Placeholder for actual company processing (Task 11)
    if args.company:
        siya_logger.info(f"Would now process single company: {args.company} using {args.provider}/{args.model}")
        # Example call (will be implemented in Task 11)
        # extracted_data = ai_instance.extract_company_info(args.company, args.model)
        # siya_logger.info(f"Extracted data: {extracted_data}")
    elif args.csv_file:
        siya_logger.info(f"Would now process companies from CSV: {args.csv_file} using {args.provider}/{args.model}")
        # Example call (will be implemented in Task 11)
        # companies = load_companies_from_csv(args.csv_file)
        # for company in companies:
        #     extracted_data = ai_instance.extract_company_info(company, args.model)
        #     siya_logger.info(f"Extracted data for {company}: {extracted_data}")

if __name__ == "__main__":
    main()
