# SIGA Setup Guide

This guide provides detailed instructions to set up your development environment for the Subsidiary Intelligence Gathering Agent (SIGA) application.

### 1. Conda Environment Setup

SIGA uses Conda for environment management and `pip` for package installation. Follow these steps to set up your environment:

1. **Install Conda:** If you don't have Conda (Anaconda or Miniconda) installed, download it from [Anaconda's official website](https://www.anaconda.com/products/distribution).

2. **Navigate to Project Root:**

cd /path/to/your/siga/project/


3. **Create the Conda Environment:**

conda create -n siga_env python=3.9


4. **Activate the Environment:**

conda activate siga_env


5. **Install Dependencies:**

pip install -r requirements.txt


### 2. API Keys and Configuration (`.env` file)

SIGA uses environment variables to manage API keys and other sensitive configurations. This keeps your credentials secure and separate from the codebase.

1. **Create your `.env` file:**

* In the root of the `siga` project directory, create a new file named `.env` (note: no `.example` suffix).

* This file should **NOT** be committed to Git (it's already in `.gitignore`).

2. **Copy contents from `.env.example`:**

* Copy all the content from the `.env.example` file into your newly created `.env` file.

3. **Replace placeholders with your actual keys:**

* For each AI service you intend to use, replace `your_openai_api_key_here`, `your_google_api_key_here`, etc., with your actual API keys.

* Set the appropriate `_PREFERRED_MODEL` and `_BASE_URL` (for Ollama) for the models you wish to use.

* Ensure `COMPANY_RESEARCH_TIMEOUT_SECONDS` is set to `60` (or your desired value).

Example `.env` content (with actual values):

```ini
# .env

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_PREFERRED_MODEL=gpt-4o

GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_PREFERRED_MODEL=gemini-pro

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_PREFERRED_MODEL=llama2

COMPANY_RESEARCH_TIMEOUT_SECONDS=60
LOG_LEVEL=INFO

# --- Prompt Configuration ---
DEFAULT_PROMPT_VERSION=subsidiary_research_v1
3. Running SIGA
Once your environment is set up and .env is configured, you can run SIGA from the project root directory.

To run in interactive mode for a single company:

Bash

python -m src.main --interactive --company "Coca-Cola"
You will be prompted to choose an AI provider, then a model, and then a prompt version.

To run in non-interactive mode for a single company:

Bash

python -m src.main --provider openai --model gpt-4o-mini --company "Nike" --prompt_version subsidiary_research_v1
To run in interactive mode with a CSV file (batch processing):

Bash

python -m src.main --interactive --csv_file "data/your_companies.csv"
(Ensure data/your_companies.csv exists and has company names in the first column).

Output:

Processed data will be saved to data/output.xlsx (Excel file with "Run Summary" and "Detailed Extracted Data" sheets) and raw JSON outputs will be saved to data/json_outputs/.