# Environment Setup Guide for AI Agents Course

This guide will walk you through setting up the necessary environment for the AI Agents course. You'll learn how to create a virtual environment, install the required dependencies, and configure your environment for development.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setting Up a Python Virtual Environment](#setting-up-a-python-virtual-environment)
  - [macOS and Linux](#macos-and-linux)
  - [Windows](#windows)
- [Installing Requirements](#installing-requirements)
- [Setting Up Environment Variables](#setting-up-environment-variables)
- [Jupyter Notebook Setup](#jupyter-notebook-setup)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, make sure you have the following installed on your system:

- Python 3.8 or higher. Python download link (https://www.python.org/downloads/)
- pip (Python package installer)
- Git (for cloning the repository)

You can check your Python version by running:

```bash
python --version
# or
python3 --version
```

## Setting Up a Python Virtual Environment

Virtual environments allow you to manage project-specific dependencies without affecting other Python projects on your system.

### macOS and Linux

1. Open your terminal.

2. Navigate to the project directory:

```bash
cd path/to/agentic-ai-workflows
```

3. Create a virtual environment:

```bash
python3 -m venv venv
```

4. Activate the virtual environment:
Mac:
```bash
source venv/bin/activate
```

Once activated, your terminal prompt should change to indicate you're now working inside the virtual environment.

5. To deactivate the virtual environment when you're done working:

```bash
source deactivate
```

### Windows

1. Open Command Prompt or PowerShell.

2. Navigate to the project directory:

```cmd
cd path\to\ai-agents-lessons
```

3. Create a virtual environment:

```cmd
python -m venv venv
```

4. Activate the virtual environment:

In Command Prompt:
```cmd
venv\Scripts\activate
```

In PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

If you encounter an execution policy error in PowerShell, you might need to set the execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

5. To deactivate the virtual environment when you're done working:

```cmd
deactivate
```

## Installing Requirements

With your virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

This will install the following packages:
- ipykernel (for Jupyter notebooks)
- pandas, numpy (for data manipulation)
- streamlit (for creating web applications)
- openai (for accessing OpenAI's models)
- python-dotenv (for environment variable management)
- requests, uuid, faker (utilities)
- fastapi, uvicorn (for API development)
- mlflow (for ML experiment tracking)
- PyPDF2 (for PDF handling)
- sqlalchemy (for database interactions)
- llama-index (for vector store and retrieval)
- IPython (enhanced interactive Python shell)
- openpyxl, xlrd (for Excel file handling)
- docling (for document processing)

## Setting Up Environment Variables

Many of the lessons involve working with external APIs that require authentication. Create a `.env` file in the root directory of the project:

```bash
touch .env  # macOS/Linux
# or
type nul > .env  # Windows
```

Add your API keys and other environment variables to this file:

```
OPENAI_API_KEY=your_openai_api_key
# Add other API keys as needed
```

**Important:** Never commit this file to version control. The `.gitignore` file should already be set up to ignore `.env` files.

## Jupyter Notebook Setup

This course includes Jupyter notebooks for interactive learning. To set up Jupyter with your virtual environment:

1. With your virtual environment activated, install the ipykernel package (should already be installed from requirements.txt):

```bash
pip install ipykernel
```

2. Register your virtual environment as a Jupyter kernel:

```bash
python -m ipykernel install --user --name=ai-agents-venv --display-name="AI Agents (venv)"
```

3. Launch Jupyter Notebook:

```bash
jupyter notebook
```

4. In the Jupyter interface, navigate to the lesson notebook you want to work with and select the "AI Agents (venv)" kernel from the Kernel menu.

## Troubleshooting

### Package Installation Issues

If you encounter issues installing packages:

1. Ensure your pip is up to date:

```bash
pip install --upgrade pip
```

2. If a specific package fails to install, try installing it separately:

```bash
pip install package_name
```

3. On Windows, some packages might require C++ build tools. Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) if needed.

### Virtual Environment Issues

If your virtual environment isn't working correctly:

1. Delete the virtual environment directory (venv) and create it again.

2. Ensure you're using the correct Python version.

3. On macOS, if you're using Homebrew Python, you might need to install venv separately:

```bash
pip install virtualenv
virtualenv venv
```

### Jupyter Notebook Issues

If Jupyter notebooks can't find the installed packages:

1. Verify you've activated the correct kernel ("AI Agents (venv)").

2. Reinstall the kernel:

```bash
python -m ipykernel install --user --name=ai-agents-venv --display-name="AI Agents (venv)"
```

If you encounter any other issues, please refer to the lesson README files or reach out for support.