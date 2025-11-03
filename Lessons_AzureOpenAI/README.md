# AI Agents Lessons - Comprehensive Tutorial Series

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Overview

**Empowering the Future: Building Agentic AI Applications** is a comprehensive, hands-on course that takes learners from foundational concepts of Large Language Models (LLMs) to building sophisticated multi-agent systems and deploying them into production. This repository contains practical coding exercises, examples, and projects using Python and LLM API endpoints.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Course Structure](#course-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Prerequisites

### Software Requirements
- **Python**: 3.9 or higher
- **IDE**: VS Code (recommended) or PyCharm Community Edition
- **Docker Desktop**: For containerization (required for production lessons)
- **Git**: For version control

### Hardware Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB+ free space
- **Internet**: Stable connection for API calls

### API Access
You'll need an API key from one of these providers:
- OpenAI API
- Google Gemini API
- Azure OpenAI Service

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-agents-lessons
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Start with Lesson 1**
   ```bash
   cd lesson_1_environment_setup
   # Follow the Environment-Setup.md guide
   ```

## 📚 Course Structure

### Core Lessons

| Lesson | Topic | Key Technologies |
|--------|-------|------------------|
| **Lesson 1** | [Environment Setup](lesson_1_environment_setup/) | Python, Virtual Environments, API Configuration |
| **Lesson 2** | [Chatbot Basics](lesson_2_chatbot_basics/) | OpenAI API, Basic Prompting, Function Calling |
| **Lesson 3** | [RAG & Web Access](lesson_3_rag_web_access/) | Brave Search API, Web Scraping, Information Retrieval |
| **Lesson 4** | [Text-to-SQL](lesson_4_text_to_sql/) | SQLite, Natural Language to SQL, Database Integration |
| **Lesson 5** | [Document RAG](lesson_5_document_rag/) | LlamaIndex, Vector Search, Document Processing |
| **Lesson 6** | [Multi-Agent Systems](lesson_6_multi_agent_systems/) | Agent Orchestration, Inter-agent Communication |
| **Lesson 7** | [Evaluation Metrics](lesson_7_evaluation_metrics/) | Performance Testing, Quality Metrics, Benchmarking |
| **Lesson 8** | [API Deployment](lesson_8_api_deployment/) | FastAPI, REST APIs, Service Architecture |
| **Lesson 9** | [Production Deployment](lesson_9_production/) | Docker, Cloud Deployment, Monitoring |

### Additional Components

- **Data**: Sample datasets, databases, and test cases
- **Utils**: Shared utilities for API interactions, evaluation, and visualization

## 🛠 Installation

### Method 1: Standard Installation

```bash
# Clone repository
git clone <repository-url>
cd ai-agents-lessons

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Using Conda

```bash
# Create conda environment
conda create -n ai-agents python=3.10
conda activate ai-agents

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

1. **Create environment file**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to `.env`**
   ```env
    # Azure OpenAI Configuration
    AZURE_OPENAI_KEY=your_azure_openai_key_here
    AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
    AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
    AZURE_OPENAI_VERSION=2024-12-01-preview
    AZURE_OPENAI_MODEL=gpt-4o-mini

    # Azure OpenAI Embeddings Configuration
    AZURE_OPENAI_EMBEDDINGS_API_KEY=your_embeddings_api_key_here
    AZURE_OPENAI_EMBEDDINGS_ENDPOINT=https://your-embeddings-resource.openai.azure.com/
    AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME=your_embeddings_deployment
    AZURE_OPENAI_EMBEDDINGS_API_VERSION=2024-02-01
    AZURE_OPENAI_EMBEDDINGS_MODEL=text-embedding-3-large
   ```

3. **Verify setup**
   ```bash
   python -c "import openai; print('Setup successful!')"
   ```

## 💻 Usage

### Running Jupyter Notebooks

```bash
# Start Jupyter Lab
jupyter lab

# Or Jupyter Notebook
jupyter notebook
```

### Running Examples

```bash
# Lesson 3 example
cd lesson_3_rag_web_access/examples
python example_3.py

# Lesson 4 example
cd lesson_4_text_to_sql/examples
python example_4.py
```

### Running the Multi-Agent Chatbot

```bash
cd multi_agent_chatbot
streamlit run app.py
```

## ✨ Features

### 🤖 AI Agent Capabilities
- **Web Search Agent**: Real-time information retrieval using Brave Search
- **SQL Agent**: Natural language to SQL query conversion
- **Document Agent**: RAG-based document processing and Q&A
- **Router Agent**: Intelligent request routing to appropriate agents

### 🔧 Technical Features
- Function calling with OpenAI/Azure OpenAI
- Vector embeddings and semantic search
- Database integration (SQLite, SQL Server)
- Document processing (PDF, TXT, DOCX)
- API deployment with FastAPI
- Docker containerization

### 📊 Evaluation & Monitoring
- Performance metrics and benchmarking
- Error handling and logging
- API monitoring and health checks
- Conversation memory management

## 🏗️ Project Structure

```
ai-agents-lessons/
├── 📁 lesson_1_environment_setup/    # Environment configuration
├── 📁 lesson_2_chatbot_basics/       # Basic chatbot implementation
├── 📁 lesson_3_rag_web_access/       # Web search and RAG
├── 📁 lesson_4_text_to_sql/          # SQL generation and execution
├── 📁 lesson_5_document_rag/         # Document processing
├── 📁 lesson_6_multi_agent_systems/  # Multi-agent orchestration
├── 📁 lesson_7_evaluation_metrics/   # Testing and evaluation
├── 📁 lesson_8_api_deployment/       # API development
├── 📁 lesson_9_production/           # Production deployment
├── 📁 data/                          # Sample data and databases
├── 📁 utils/                         # Shared utilities
├── 📄 requirements.txt               # Python dependencies
└── 📄 README.md                      # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: Check individual lesson READMEs for detailed instructions
- **Examples**: Refer to the `examples/` directories in each lesson

## 🌟 Acknowledgments

- OpenAI for GPT models and API
- LlamaIndex for RAG capabilities
- Brave Search for web search functionality
- The open-source AI community
