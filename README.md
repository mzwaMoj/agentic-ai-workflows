# Building Agentic AI Applications - Beginner's Guide

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://platform.openai.com/)
[![Azure](https://img.shields.io/badge/Azure-OpenAI-blue.svg)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

## 🎯 Overview

Welcome! This repository is your **friendly, beginner-focused guide** to building AI agents from scratch. Whether you're using OpenAI's API or Azure OpenAI, you'll learn to create intelligent applications that can search the web, query databases, process documents, and much more.

### What You'll Learn

- 🤖 **Build AI Agents** - Create chatbots, search agents, and database assistants
- 🔧 **Use Modern APIs** - Work with OpenAI's latest response format and tool calling
- 🚀 **Go From Zero to Production** - Start with basics, end with deployable applications
- 🎓 **Hands-On Learning** - Every lesson includes working code and Jupyter notebooks

### Architecture Overview

Here's what a multi-agent system looks like:

https://github.com/user-attachments/assets/your-video-id-here

> **Note**: Upload `presentation/ArchitectureView.mov` to your GitHub repository's Issues or PR, then replace the URL above with the generated link.

## 📚 What's Inside

This repository contains **two parallel lesson tracks** - pick the one that matches your API provider:

### 📂 Lessons_OpenAI
Complete tutorials using **OpenAI's API** (GPT-4+)
- Uses the new `client.responses.create()` format
- Modern tool calling patterns
- Direct OpenAI API integration

### 📂 Lessons_AzureOpenAI  
Identical lessons using **Azure OpenAI Service**
- Enterprise-grade deployment
- Same capabilities, Azure integration
- Follows Azure authentication patterns

**Both tracks cover the same material** - choose based on your API access!


## �️ Learning Path

Each lesson builds on the previous one, taking you from beginner to building production-ready AI agents.

| Lesson | What You'll Build | Key Concepts |
|--------|-------------------|--------------|
| **1. Environment Setup** | Development environment | Python, virtual environments, API keys |
| **2. Chatbot Basics** | Your first AI chatbot | Response API, prompting, conversations |
| **3. Web Search Agent** | Agent that searches the web | Tool calling, function definitions, API integration |
| **4. Text-to-SQL Agent** | Natural language database queries | SQLite, schema understanding, query generation |
| **5. Document Q&A Agent** | Ask questions about documents | RAG, vector search, embeddings |
| **6. Multi-Agent System** | Multiple specialized agents | Agent orchestration, routing, coordination |
| **7. Evaluation & Testing** | Measure agent performance | Metrics, testing, quality assurance |
| **8. API Deployment** | Deploy as REST API | FastAPI, endpoints, service architecture |
| **9. Production Ready** | Deploy to production | Docker, monitoring, scaling |

### 🎓 Prerequisites

**What you need to know:**
- Basic Python (variables, functions, loops)
- How to use a terminal/command prompt
- Basic understanding of APIs (helpful but not required)

**What you need to have:**
- Python 3.9 or higher installed
- An OpenAI API key OR Azure OpenAI access
- A code editor (VS Code recommended)
- About 2GB free disk space


## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### Step 2: Choose Your Track

Pick OpenAI or Azure OpenAI based on what you have access to:

**For OpenAI API:**
```bash
cd Lessons_OpenAI
```

**For Azure OpenAI:**
```bash
cd Lessons_AzureOpenAI
```

### Step 3: Follow the Setup Guide

Each folder has its own `README.md` with detailed setup instructions:

1. Create a virtual environment
2. Install dependencies
3. Configure your API keys
4. Start with Lesson 1

### Step 4: Start Learning!

Open Lesson 1 and follow along. Each lesson includes:
- 📓 Jupyter notebooks with explanations
- 💻 Working code examples
- ✅ Exercises to practice
- 🎯 A project to build

## 🔑 What Makes This Different?

### ✨ Beginner Friendly
- **No prior AI experience needed** - We start from the basics
- **Step-by-step explanations** - Every concept is explained clearly
- **Working examples** - All code is tested and ready to run
- **Learn by doing** - Build real projects in every lesson

### 🎯 Practical Focus
- **Real-world projects** - Build agents you can actually use
- **Modern patterns** - Learn the latest API formats and best practices
- **Production ready** - Go beyond tutorials to deployable applications
- **Two API options** - Works with OpenAI or Azure OpenAI

### 🚀 Progressive Learning
- **Start simple** - Basic chatbot in Lesson 2
- **Add complexity** - Web search, databases, documents
- **Combine skills** - Multi-agent systems in Lesson 6
- **Deploy it** - Production deployment guide in Lesson 9


## 🤖 What You'll Build

Throughout these lessons, you'll create increasingly sophisticated AI agents:

### Lesson 2: Simple Chatbot
```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4",
    input="Hello! Tell me a joke."
)
print(response.output_text)
```

### Lesson 3: Web Search Agent
An agent that can search the internet and answer questions with current information.

### Lesson 4: Database Agent
Convert natural language to SQL:
- "Show me top 5 customers by spending" → SQL query → Results

### Lesson 5: Document Agent  
Ask questions about your PDF documents using RAG (Retrieval Augmented Generation).

### Lesson 6: Multi-Agent System
Multiple specialized agents working together:
- Router agent decides which specialist to use
- Web agent for current events
- SQL agent for database queries
- Document agent for company documents

### Lessons 7-9: Production Deployment
Deploy your agents as APIs with monitoring, testing, and Docker containers.


## �️ Repository Structure

```
├── Lessons_OpenAI/              # Complete course using OpenAI API
│   ├── lesson_1_environment_setup/
│   ├── lesson_2_chatbot_basics/
│   ├── lesson_3_rag_web_access/
│   ├── lesson_4_text_to_sql/
│   ├── lesson_5_document_rag/
│   ├── lesson_6_multi_agent_systems/
│   ├── lesson_7_evaluation_metrics/
│   ├── lesson_8_api_deployment/
│   ├── lesson_9_production/
│   └── requirements.txt
│
├── Lessons_AzureOpenAI/         # Same course using Azure OpenAI
│   ├── lesson_1_environment_setup/
│   ├── lesson_2_chatbot_basics/
│   └── ... (same structure as above)
│
└── README.md                    # You are here!
```

## 🎓 Learning Tips

### For Complete Beginners
1. **Start with Lesson 1** - Don't skip the setup!
2. **Type the code yourself** - Don't just copy-paste
3. **Experiment** - Change values and see what happens
4. **Take breaks** - These are complex concepts
5. **Join the community** - Ask questions, share what you build


## 🌟 What You'll Master

By the end of this course, you'll be able to:

✅ Build conversational AI chatbots with memory  
✅ Create agents that search the web for real-time information  
✅ Convert natural language to database queries  
✅ Build document Q&A systems using RAG  
✅ Orchestrate multiple AI agents working together  
✅ Test and evaluate agent performance  
✅ Deploy agents as production APIs  
✅ Use modern tool calling patterns  
✅ Handle errors and edge cases gracefully  
✅ Monitor and scale AI applications  

## 📖 Additional Resources

**Official Documentation:**
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

**Community:**
- [OpenAI Community Forum](https://community.openai.com/)
- Open an issue on this repository for help

**Further Learning:**
- [OpenAI Cookbook](https://cookbook.openai.com/) - Advanced examples
- [LangChain Documentation](https://python.langchain.com/) - Alternative framework

## 🤝 Contributing

Found a bug? Have a suggestion? Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - use it freely for learning or commercial projects!


---

**This guide is a work in progress. Additional models including opensource models will be added** 
