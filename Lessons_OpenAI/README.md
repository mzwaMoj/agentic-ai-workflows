# AI Agents with OpenAI - Tutorial Series

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://platform.openai.com/)

## 🚀 Overview

Learn to build AI agents using OpenAI's latest API features, including the new **Responses API** format and **tool calling**. This hands-on course covers everything from basic chatbots to advanced multi-agent systems with database integration.

### What's New with OpenAI

This course uses OpenAI's modern API structure:

**New Response Format:**
```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input="Your prompt here"
)

print(response.output_text)
```

**Tool Calling (Function Calling):**
```python
tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get weather for a location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}]

response = client.responses.create(
    model="gpt-4.1",
    input=input_list,
    tools=tools
)
```

## 📋 Prerequisites

- **Python**: 3.9 or higher
- **OpenAI API Key**: Get one at [platform.openai.com](https://platform.openai.com/)
- **IDE**: VS Code or Jupyter Notebook
- **Basic Python knowledge**: Variables, functions, loops


## 🚀 Quick Start

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd Lessons_OpenAI

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure OpenAI API

1. Get your API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

2. Create a `.env` file:
   ```bash
   touch .env  # Mac/Linux
   # or
   type nul > .env  # Windows
   ```

3. Add your API key:
   ```env
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4.1
   OPENAI_EMBEDDING_MODEL=text-embedding-3-large

   BRAVE_SEARCH_API_KEY= your_brave_search_api_key
   ```

### Step 3: Test Your Setup

Run this simple test:

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="gpt-4.1",
    input="Say hello!"
)

print(response.output_text)
```

If you see a response, you're ready to go! 🎉

### Step 4: Start Learning

Begin with Lesson 2 and work your way through

## 📚 Course Structure

Each lesson builds on the previous one, teaching you to create increasingly sophisticated AI agents.

| Lesson | Topic | What You'll Build |
|--------|-------|-------------------|
| **Lesson 1** | Environment Setup | Development environment configuration |
| **Lesson 2** | Chatbot Basics | Simple chatbot with OpenAI's response API |
| **Lesson 3** | Web Search Agent | Agent that searches the web and answers questions |
| **Lesson 4** | Text-to-SQL Agent | Convert natural language to SQL queries |
| **Lesson 5** | Document Q&A Agent | Ask questions about your documents |
| **Lesson 6** | Multi-Agent System | Multiple agents working together |
| **Lesson 7** | Evaluation & Testing Guide| Measure and improve agent performance |
| **Lesson 8** | API Deployment Guide| Deploy your agent as a REST API |
| **Lesson 9** | Production Ready Guide| Docker, monitoring, and scaling |

### Key Concepts You'll Learn

✅ **OpenAI Responses API** - Modern API format with `client.responses.create()`  
✅ **Tool Calling** - Let AI agents call your Python functions  
✅ **Function Definitions** - Define tools for the AI to use  
✅ **Multi-turn Conversations** - Maintain context across interactions  
✅ **Agent Orchestration** - Coordinate multiple specialized agents  
✅ **Error Handling** - Build robust, production-ready agents


## � Code Examples

### Basic Response API

```python
from openai import OpenAI
client = OpenAI()

# Simple completion
response = client.responses.create(
    model="gpt-4",
    input="Explain quantum computing in simple terms"
)
print(response.output_text)
```

### Tool Calling (Function Calling)

```python
from openai import OpenAI
import json

client = OpenAI()

# 1. Define your tool
tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current weather for a location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, e.g., San Francisco"
            }
        },
        "required": ["location"]
    }
}]

# 2. Create input list
input_list = [
    {"role": "user", "content": "What's the weather in Tokyo?"}
]

# 3. Call the API
response = client.responses.create(
    model="gpt-4",
    tools=tools,
    input=input_list
)

# 4. Handle function calls
input_list += response.output

for item in response.output:
    if item.type == "function_call":
        # Execute your function
        args = json.loads(item.arguments)
        result = get_weather(args["location"])
        
        # Return result to AI
        input_list.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(result)
        })

# 5. Get final response
final_response = client.responses.create(
    model="gpt-4",
    tools=tools,
    input=input_list
)

print(final_response.output_text)
```

### Multi-turn Conversation

```python
input_list = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the capital of France?"}
]

response = client.responses.create(model="gpt-4", input=input_list)
input_list += response.output

# Continue conversation
input_list.append({"role": "user", "content": "What's its population?"})
response = client.responses.create(model="gpt-4", input=input_list)
print(response.output_text)
```


## 🗂️ Project Structure

```
Lessons_OpenAI/
├── lesson_1_environment_setup/   # Getting started
├── lesson_2_chatbot_basics/      # Basic chatbot with responses API
├── lesson_3_rag_web_access/      # Web search agent
├── lesson_4_text_to_sql/         # Database query agent
├── lesson_5_document_rag/        # Document Q&A agent
├── lesson_6_multi_agent_systems/ # Multi-agent orchestration
├── lesson_7_evaluation_metrics/  # Testing & evaluation
├── lesson_8_api_deployment/      # REST API deployment
├── lesson_9_production/          # Production deployment
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔑 Key Dependencies

- **openai** - OpenAI API client
- **python-dotenv** - Environment variable management
- **jupyter** - Interactive notebooks
- **pandas** - Data manipulation
- **sqlite3** - Database (built-in)
- **fastapi** - API framework (later lessons)

## 🆘 Common Issues

### "Module not found" error
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall requirements
pip install -r requirements.txt
```

### API Key not working
```bash
# Check .env file exists and has your key
cat .env  # Mac/Linux
type .env  # Windows

# Verify it loads correctly
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### Rate limit errors
- You've exceeded your OpenAI API quota
- Add billing information at [platform.openai.com/account/billing](https://platform.openai.com/account/billing)
- Or wait and try again later

## 🌟 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI Cookbook](https://cookbook.openai.com/)
- [OpenAI Community Forum](https://community.openai.com/)

## 📝 License

MIT License - see LICENSE file for details

---

