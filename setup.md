### 1. Conda Environment Setup

SIGA uses Conda for environment management and `pip` for package installation. Follow these steps to set up your environment:

1.  **Install Conda:** If you don't have Conda (Anaconda or Miniconda) installed, download it from [Anaconda's official website](https://www.anaconda.com/products/distribution).
2.  **Navigate to Project Root:**
    ```bash
    cd /path/to/your/siga/project/
    ```
3.  **Create the Conda Environment:**
    ```bash
    conda create -n siga_env python=3.9
    ```
4.  **Activate the Environment:**
    ```bash
    conda activate siga_env
    ```
5.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```