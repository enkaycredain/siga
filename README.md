# Subsidiary Intelligence Gathering Agent (SIGA)

## Overview

SIGA (Subsidiary Intelligence Gathering Agent) is an intelligent command-line application designed to extract structured information about companies and their subsidiaries. It leverages the internal knowledge of various large language models (LLMs) from providers like OpenAI, Google AI (Gemini), and local Ollama instances.

The agent focuses specifically on gathering:

* **Subsidiary names**

* **Their geographical locations**

* **Sources of this information (if available from the LLM's knowledge)**

SIGA is built for robustness, featuring dynamic LLM and prompt selection, rate limiting, and comprehensive logging. It outputs data into a well-organized Excel file with linked summary and detailed sheets, and also saves raw JSON responses for auditing.

---

## Documentation

For detailed information on setting up, running, and contributing to SIGA, please refer to the following documents in the `docs/` folder:

* [**Setup Guide**](docs/SETUP.md): Instructions for environment setup, dependencies, and configuration.

* [**Requirements and Tasks**](docs/Requirements%20and%20Tasks.md): A comprehensive list of project requirements and a detailed breakdown of development tasks.

---

## Quick Start (after setup)

Once you have followed the [Setup Guide](docs/SETUP.md) and configured your `.env` file:

To run SIGA in interactive mode for a single company:

```bash
python -m src.main --interactive --company "Coca-Cola"