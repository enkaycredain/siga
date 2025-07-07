

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