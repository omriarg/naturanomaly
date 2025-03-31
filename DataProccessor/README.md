# software house project
This repository belongs to the software house project on llm 
# Miniconda Installation and Environment Setup (Windows)

## 1. Install Miniconda

1. Download the Miniconda installer for Windows from [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
2. Run the installer and follow the instructions.
   - Ensure "Add Miniconda to my PATH" is selected.

## 2. Create Environment from `environment.yml`

1. Open **Command Prompt** (or **Anaconda Prompt** if installed).
2. Navigate to the project directory where `environment.yml` is located.
3. Run anaconda prompt:
   ```bash
   conda env create -f environment.yml
   ```

## 3. If `conda` Environment Setup Fails: Use `pip install`

If the `conda` environment creation doesn’t work or you prefer using `pip`, follow these steps:

1. Create a new environment with a specific Python version (e.g., Python 3.11):
   ```bash
   conda create --name <environment_name> python=3.11
   ```
   Replace `<environment_name>` with your desired environment name and `3.11` with the version of Python you need.

2. Activate the environment:
   ```bash
   conda activate <environment_name>
   ```

3. Install the required dependencies manually using `pip`:
   - If you have a `requirements.txt` file:
     ```bash
     pip install -r requirements.txt
     ```
   - If you don’t have `requirements.txt`, manually install the required packages with:
     ```bash
     pip install <package1> <package2> ...
     ```

## 4. Activate the Environment

To activate your environment:
```bash
conda activate <environment_name>
```

Replace `<environment_name>` with the name of your environment.

## 5. Deactivate the Environment

To deactivate the environment:
```bash
conda deactivate
```

---

# Ollama and Llama 3.2 Installation Guide (Windows)

## Install Ollama
1. Download the [Ollama Windows installer](https://ollama.com/download).
2. Run the installer and follow the instructions.

## Install Llama 3.2
in the command line run 
```bash
ollama run llama3.2
```


You’re all set! Start working in your Miniconda environment using main.py


