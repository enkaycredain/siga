

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

* [x] Task 6: Configuration Loading & CLI for Provider Selection (Part 1 - Improved UX)
    * **Objective:** Load environment variables from `.env` and allow the user to select the desired AI *provider* via the CLI with improved interactive experience (numbered choices, default highlighting).
    * **Details:**
        * Implement `python-dotenv` for loading `.env` variables (already done).
        * Create `src/config_loader.py` to manage configuration (already done).
        * Update `src/main.py` CLI entry point:
            * Improved interactive prompt for provider selection: present numbered choices, highlight preferred default from `.env`.
            * This part will NOT yet dynamically list *models* from providers; that comes after Task 7/8.
        * Ensure `python -m src.main` is clearly documented as the way to run the application.
* [x] Task 7: Abstract AI Interface with Model Listing (Completed)
    * **Objective:** Define a common interface for AI models, *including a method to list available models from the provider*.
    * **Details:**
        * Create `src/ai_models/base.py`.
        * Define an abstract base class (ABC) with methods like `extract_company_info(self, company_name: str) -> dict` and `list_available_models(self) -> list[str]`.
        * Include a `get_preferred_model(self) -> str` property/method to retrieve the preferred default model for that provider (from config).
* [x] Task 8: OpenAI Integration (Initial: `extract_company_info` & `list_available_models`) (Completed)
    * **Objective:** Implement OpenAI concrete class supporting information extraction and model listing.
    * **Details:**
        * Create `src/ai_models/openai_model.py`.
        * Implement `OpenAIModel` adhering to the interface.
        * Implement `list_available_models()` using OpenAI's API.
        * Implement a basic `extract_company_info()` (prompt engineering can be refined later).
        * Add `openai` library to `environment.yml`.
* [x] Task 6 (Part 2 - Complete Dynamic Model Selection) (Completed)
    * **Objective:** Revisit `src/main.py` to fully integrate dynamic model listing and selection after provider choice.
    * **Details:**
        * Call `ai_instance.list_available_models()` after provider selection.
        * Present the discovered models to the user (numbered, with preferred default highlighted).
        * Allow the user to select a specific model.
* [x] Task 9: Google AI (Gemini) Integration (with Model Listing) (Completed)
    * **Objective:** Implement Google AI concrete class, including its `list_available_models` method.
    * **Details:**
        * Create `src/ai_models/google_ai_model.py`.
        * Implement `GoogleAIModel` adhering to the interface.
        * Implement `list_available_models()` using Google AI's API.
        * Implement a basic `extract_company_info()` (prompt engineering can be refined later).
        * Add `google-generativeai` library to `environment.yml`.
* [x] Task 10: Ollama/Oobabooga Integration (with Model Listing) (Completed)
    * **Objective:** Implement Ollama/Oobabooga concrete class, including its `list_available_models` method.
    * **Details:**
        * Create `src/ai_models/ollama_model.py`.
        * Implement `OllamaModel` adhering to the interface.
        * Implement `list_available_models()` using Ollama's API (requires `requests` or `ollama` client).
        * Implement a basic `extract_company_info()` (prompt engineering can be refined later).
        * Add `requests` (and/or `ollama`) library to `environment.yml`.
* [x] Task 11: Core Agent Orchestration (Single Company Processing) (Completed)
    * **Objective:** Build the main agent logic to process a single company using the selected AI model, handle timeouts, and save output to CSV.
    * **Details:**
        * Update `src/main.py`.
        * Instantiate the chosen AI model.
        * Implement a `process_company` function that calls `ai_instance.extract_company_info`.
        * Implement the 1-minute timeout for AI calls.
        * Implement CSV output logic:
            * Ensure the output CSV file (`output.csv` in `data/`) is created if it doesn't exist, with a header.
            * Append each company's extracted data (flattened) along with `Date Time of Run`, `AI Model Chosen`, and `Prompt Used` to the CSV.
        * Handle errors by logging and skipping the company, as per requirements.

---

## Phase 3: Batch Processing & Robustness

This phase focuses on enabling SIYA to process multiple companies from a CSV file, manage workload, and implement robust failure recovery.

* [ ] Task 12: CSV Input Processing
    * **Objective:** Read company names from a CSV file and prepare them for processing.
    * **Details:**
        * Create a new utility function (e.g., in `src/utils.py`) to read a list of company names from a CSV file.
        * Integrate this function into `src/main.py` when `--csv_file` argument is provided.
        * Add `pandas` to `environment.yml` for robust CSV reading.
* [ ] Task 13: Progress Tracking & Failure Recovery
    * **Objective:** Implement a mechanism to track completed companies and resume processing from the last failed point.
    * **Details:**
        * Implement a simple persistence mechanism (e.g., a small JSON file in `data/` or a dedicated `progress.json`) to store the list of successfully processed companies.
        * Before processing a company, check if it's already in the "completed" list. If so, skip it.
        * After a successful company processing, add its name to the "completed" list and save the progress.
        * Ensure this mechanism is robust to application restarts.
* [ ] Task 14: Workload Management (Rate Limiting for Batch)
    * **Objective:** Ensure the agent manages the workload and respects the 1-minute per company research constraint when processing multiple companies.
    * **Details:**
        * While the `process_single_company` already has a timeout, for batch processing, we need to ensure calls are spaced out if necessary (though the 1-minute timeout per call inherently provides some spacing).
        * This task will primarily involve ensuring the loop over companies in `main.py` respects the overall rate limit. Given the 1-minute timeout per company, this might mostly involve just sequential processing without explicit delays between companies, as the timeout handles the minimum duration. We will verify this.

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