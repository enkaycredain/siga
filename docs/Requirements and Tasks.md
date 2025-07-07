# SIGA Requirements and Tasks

This document outlines the detailed functional and non-functional requirements for the Subsidiary Intelligence Gathering Agent (SIGA) solution, along with a breakdown of its development tasks.

---

## Project Tasks

This section tracks the progress of the SIGA development.

### Phase 1: Project Setup and Core Environment

* [x] Task 1: Project Repository Initialization (Completed)
* [x] Task 2: `README.md` Creation & Requirements Documentation (Completed)
* [x] Task 3: Conda Environment Setup (Completed - *Updated for pip requirements*)
    * **Objective:** Create a dedicated Conda environment for SIGA, install initial dependencies using `pip` from `requirements.txt`, and document the setup process.
    * **Details:**
        * Create a new Conda environment.
        * Activate the Conda environment.
        * Generate a `requirements.txt` file from `environment.yml`.
        * Install dependencies using `pip install -r requirements.txt`.
        * Update `SETUP.md` with these instructions.
* [x] Task 4: `.env` File for Configuration (Completed)
* [x] Task 5: Basic Logging Configuration (Completed)

### Phase 2: Core Agent Logic & AI Integration

* [x] Task 6: Configuration Loading & CLI for Provider Selection (Part 1 - Improved UX) (Completed)
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
        * Define an abstract base class (ABC) with methods like `extract_company_info(self, company_name: str, model_name: str, user_template: str, system_message: str) -> dict` and `list_available_models(self) -> list[str]`.
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
    * **Objective:** Build the main agent logic to process a single company using the selected AI model, handle timeouts, and save output to **Excel (two sheets, linked by Run ID)**.
    * **Details:**
        * Update `src/main.py`.
        * Instantiate the chosen AI model.
        * Implement a `process_company` function that calls `ai_instance.extract_company_info`.
        * Implement the 1-minute timeout for AI calls.
        * Implement **Excel output logic using `openpyxl`**:
            * Ensure the output Excel file (`output.xlsx` in `data/`) is created if it doesn't exist.
            * Append data to two sheets: "Run Summary" and "Detailed Extracted Data", with appropriate headers.
            * **Add a unique `Run ID` to link entries between the two sheets.**
        * Handle errors by logging and skipping the company, as per requirements.

---

## Phase 3: Batch Processing & Robustness

This phase focuses on enabling SIGA to process multiple companies from a CSV file, manage workload, and implement robust failure recovery.

* [x] Task 12: CSV Input Processing (Completed)
    * **Objective:** Read company names from a CSV file and prepare them for processing.
    * **Details:**
        * Create a new utility file (`src/utils.py`) to contain helper functions.
        * Implement a function `read_companies_from_csv(file_path: str) -> List[str]` in `src/utils.py` to read a list of company names from the first column of a CSV file.
        * Integrate this function into `src/main.py` when `--csv_file` argument is provided, to get the list of companies.
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
        * This task will primarily involve just sequential processing without explicit delays between companies, as the timeout handles the minimum duration. We will verify this.

---

## Phase 4: Enhanced Output & Prompt Management

This phase focuses on improving SIGA's output formats and introducing a flexible system for managing AI prompts.

* [x] Task 15: Implement Excel Sheet Linking (Run ID) (Completed)
    * **Objective:** Link the "Run Summary" and "Detailed Extracted Data" sheets in the Excel output using a unique Run ID.
    * **Details:**
        * Generate a unique `run_id` (e.g., using `uuid.uuid4()`).
        * Add a "Run ID" column to both `SUMMARY_HEADERS` and `DETAIL_HEADERS`.
        * Modify `_write_to_excel` in `src/main.py` to include this `run_id` in every row written to both sheets.
* [x] Task 16: Save Raw JSON Output per Run (Completed)
    * **Objective:** Save the raw JSON response from the AI, along with run metadata, to a dedicated JSON file for each company processed.
    * **Details:**
        * Create a new subfolder `data/json_outputs/`.
        * Implement a helper function `_save_raw_json_output` in `src/main.py` to save the raw JSON data and associated metadata (company, model, prompt, run ID) to a `.json` file.
        * Call this function within `process_single_company`.
* [x] Task 17: Externalize & Version Prompt Templates (Completed)
    * **Objective:** Move prompt templates from hardcoded strings into an external, versioned configuration file.
    * **Details:**
        * Create a `config/prompts.json` file to store multiple prompt templates, each with a version/name, including `system_message` and `user_template`.
        * Modify `src/config_loader.py` to load these prompt templates.
        * Update `src/ai_models/*.py` to accept and use the `user_template` and `system_message` from the loaded prompt data.
        * **Refine the prompt content** within this file to focus on "all direct and indirect subsidiaries" as requested.
* [x] Task 18: Interactive Prompt Selection (Completed)
    * **Objective:** Allow the user to select a prompt version interactively via the CLI.
    * **Details:**
        * Update `.env.example` with a `DEFAULT_PROMPT_VERSION` setting.
        * Modify `src/main.py` to list available prompt versions (from `config/prompts.json`), highlight the default, and allow user selection (numbered choices).
        * Pass the selected prompt version to `process_single_company`.

## Requirements v1.0

This section outlines the detailed functional and non-functional requirements for the Subsidiary Intelligence Gathering Agent (SIGA) solution.

* **Core Functionality:**
    * Agent extracts **subsidiary names, their locations (preferably address, otherwise city, country, or just country in one field), and sources (if available)** for companies.
    * Input: Single company name or CSV file with a list of companies.
    * Output: Excel file with two sheets: "Run Summary" and "Detailed Extracted Data".
* **Data Source & Hallucination Mitigation:**
    * Agent **only** uses the **AI's pre-trained knowledge/training data**.
    * **No external search** (web scraping, real-time lookups) is permitted.
    * Information will be presented "as of" the AI's training data, with a date tag in the output.
    * **AI prompts will be engineered to be precise and sharp to minimize hallucination, and will include reasoning instructions.**
* **Output Table Format (Excel - Two Sheets):**
    * **Sheet 1: "Run Summary"**
        * **Purpose:** Provides a high-level overview of each company processed, including the run metadata. Each row here represents a unique company processed in a given run.
        * **Columns:** `Run ID`, `Company Name`, `Date Time of Run`, `AI Model Chosen`, `Prompt Version Used`, `Error` (if overall processing failed), `Subsidiaries Found Count`.
    * **Sheet 2: "Detailed Extracted Data"**
        * **Purpose:** Contains the flattened, granular details about subsidiaries. Each row here corresponds to a single subsidiary entry.
        * **Columns:** `Run ID`, `Company Name`, `Subsidiary Name`, `Subsidiary Location`, `Source of Details` (if provided by AI).
    * The output will be **appended** to existing sheets in the Excel file (or create new sheets/file if they don't exist).
* **AI Model Configuration & Selection:**
    * **Support for configuring multiple AI models** (e.g., Google AI, Ollama, OpenAI).
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