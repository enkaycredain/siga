

# Subsidiary Intelligence Yielding Analyst (SIYA)

An agentic solution designed to extract comprehensive company and subsidiary information (locations, financials, news) solely from the internal knowledge of various AI models. SIYA aims to provide structured, relevant data efficiently and robustly, with user-selectable AI models and comprehensive logging.

---

## Getting Started

To set up your development environment and install dependencies, please refer to the detailed [Setup Guide](SETUP.md).

---

### Phase 1: Project Setup and Core Environment

* [x] Task 1: Project Repository Initialization (Completed)
* [x] Task 2: `README.md` Creation & Requirements Documentation (Completed)
* [x] Task 3: Conda Environment Setup (Completed)
* [x] Task 4: `.env` File for Configuration (Completed)
* [x] Task 5: Basic Logging Configuration (Completed)

### Phase 2: Core Agent Logic & AI Integration

* [ ] Task 6: Configuration Loading & Dynamic AI Model Selection
    * **Objective:** Load environment variables from `.env` and allow the user to dynamically select the desired AI model from *available* models via the CLI.
    * **Details:**
        * Implement `python-dotenv` for loading `.env` variables.
        * Create `src/config_loader.py` to manage configuration.
        * Create `src/main.py` as the CLI entry point.
        * Implement argument parsing (e.g., using `argparse`) for `--provider <provider_name>` (e.g., `openai`, `google_ai`, `ollama`) and an optional `--model <model_name>` for non-interactive use.
        * If in interactive mode (no `--model` provided), the chosen provider will be prompted, then its *available models will be dynamically fetched and listed*, with a preferred default highlighted.
        * Add `python-dotenv` to `environment.yml`.
* [ ] Task 7: Abstract AI Interface with Model Listing
    * **Objective:** Define a common interface for AI models, including a method to list available models.
    * **Details:**
        * Create `src/ai_models/base.py`.
        * Define an abstract base class (ABC) with methods like `extract_company_info(self, company_name: str) -> dict` and `list_available_models(self) -> list[str]`.
        * Consider defining a `get_preferred_model(self) -> str` property/method for the model to be highlighted as default, potentially loaded from config.
* [ ] Task 8: OpenAI Integration (with Model Listing)
    * **Objective:** Implement OpenAI concrete class supporting information extraction and model listing.
    * **Details:**
        * Create `src/ai_models/openai_model.py`.
        * Implement `OpenAIModel` adhering to the interface.
        * Implement `list_available_models()` using OpenAI's API.
        * Implement `extract_company_info()` with initial prompt engineering.
        * Add `openai` library to `environment.yml`.
* [ ] Task 9: Google AI (Gemini) Integration (with Model Listing)
    * **Objective:** Implement Google AI concrete class supporting information extraction and model listing.
    * **Details:**
        * Create `src/ai_models/google_ai_model.py`.
        * Implement `GoogleAIModel` adhering to the interface.
        * Implement `list_available_models()` using Google AI's API.
        * Implement `extract_company_info()` with initial prompt engineering.
        * Add `google-generativeai` library to `environment.yml`.
* [ ] Task 10: Ollama/Oobabooga Integration (with Model Listing)
    * **Objective:** Implement Ollama/Oobabooga concrete class supporting information extraction and model listing.
    * **Details:**
        * Create `src/ai_models/ollama_model.py`.
        * Implement `OllamaModel` adhering to the interface.
        * Implement `list_available_models()` using Ollama's API.
        * Implement `extract_company_info()` with initial prompt engineering.
        * Add `requests` (and/or `ollama` client) to `environment.yml`.
* [ ] Task 11: Core Agent Orchestration (Single Company Processing)
    * **Objective:** Build the main agent logic to process a single company using the selected AI model and apply basic error handling.
    * **Details:**
        * Modify `src/main.py` (or create an `src/agent.py` module).
        * Integrate the configuration loading and AI model selection logic.
        * Implement a function `process_single_company(company_name: str, ai_model_instance) -> dict`.
        * Call the chosen AI's `extract_company_info` method.
        * Implement initial *basic* parsing of the AI's raw text response into a structured dictionary/JSON. (This will be refined later).
        * Implement basic error handling: if the AI call fails or parsing fails for a company, log the error and return an empty/error dictionary for that company (no retries yet, as per requirement).
        * For now, print the extracted (or error) dictionary to the console.
        * Implement the 1-minute timeout per company call.

---

## Logging

SIYA provides comprehensive logging at `INFO`, `DEBUG` (for TRACE), `WARNING`, and `ERROR` levels to both the console and optional log files. Logs are timestamped and provide clear insights into agent operations.

---

## Requirements v1.0

This section outlines the detailed functional and non-functional requirements for the Subsidiary Intelligence Yielding Analyst (SIYA) solution.

* **Core Functionality:**
    * Agent extracts subsidiary lists, locations, and other related information (news, financial data) for companies.
    * Input: Single company name or CSV file with a list of companies.
    * Output: Tabular format, **always appended to a CSV file**.
* **Data Source & Hallucination Mitigation:**
    * Agent **only** uses the **AI's pre-trained knowledge/training data**.
    * **No external search** (web scraping, real-time lookups) is permitted.
    * Information will be presented "as of" the AI's training data, with a date tag in the output.
    * **AI prompts will be engineered to be precise and sharp to minimize hallucination.**
* **Output Table Format (CSV):**
    * `Company Name | Subsidiary Name | Subsidiary Location | Field Name 1 | Field Info 1 | Field Info 1 as of [Date] | Field Name N | Field Info N | Field Info N as of [Date] | Date Time of Run | AI Model Chosen | Prompt Used`
    * The output will be **appended** to an existing CSV file (or create a new one if it doesn't exist).
* **AI Model Configuration & Selection:**
    * **Support for configuring multiple AI models** (e.g., Google AI, Oobabooga/Ollama, OpenAI).
    * Configuration for **each** AI model (e.g., API keys, model names, base URLs, specific parameters) will be stored in a `.env` file.
    * **Interactive (CLI) mode:** User explicitly **chooses which AI model to use** from the configured list before running the agent.
    * **API mode (Phase 2):** The chosen AI model will be passed as a parameter/prompt to the agent.
* **Rate Limiting & Workload Management:**
    * Process one company at a time, with a maximum of **1 minute per company research call to the AI**.
    * Agent will intelligently manage the workload to avoid overwhelming AI services.
* **Failure Recovery:**
    * Agent will remember completed searches and resume from the point of failure (e.g., if 10 companies are done, it starts at the 11th).
    * **Upon error, the agent will log the error and skip that specific company**, continuing with the next. It will *not* retry for that company.
* **Logging:**
    * Comprehensive logging will be provided: `INFO`, `TRACE`, `ERROR`, and `WARNING` levels.
    * Logs will detail major steps, errors, and warnings.
* **User Interface:**
    * Interactive mode: Command Line Interface (CLI).
    * API mode: Planned for Phase 2, after initial testing and approval.
* **Technology Stack & Environment:**
    * Developed using **Python**.
    * **The project will be set up to run using Conda.**
* **Documentation:**
    * A `README.md` file will be created to document the project setup, usage, and other relevant information.