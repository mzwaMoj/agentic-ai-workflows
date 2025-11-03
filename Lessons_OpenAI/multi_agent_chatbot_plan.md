# Multi-Agent Streamlit Chatbot Plan

## Project Overview
Create a simple Streamlit chatbot powered by a multi-agent framework with 4 agents:
1. **Agent Web Search** - Handles web search queries using Brave Search API
2. **Agent SQL Queries** - Converts natural language to SQL and executes database queries
3. **Agent Document Reader** - Processes document-based queries using RAG with LlamaIndex
4. **Router Agent** - Directs user queries to the appropriate agent and returns results

## Architecture Analysis

### Current Notebook Implementations
Based on the analysis of the three notebooks:

#### Lesson 3: Web Search Agent
- Uses Brave Search API for real-time web information
- Implements function calling with OpenAI
- Has advanced multi-step research capabilities
- Key components: `brave_search()`, `extract_search_info()`, `agent_web_search()`

#### Lesson 4: SQL Agent
- Converts natural language to SQL queries
- Works with SQLite database (e-commerce data)
- Uses schema understanding for better query generation
- Key components: Database connection, schema description, SQL generation and execution

#### Lesson 5: Document RAG Agent
- Uses LlamaIndex for document processing
- Implements vector indexing and semantic search
- Has conversational memory capabilities
- Key components: Vector index creation, query engine, conversational agent

## Implementation Plan

### Step 1: Project Structure
```
multi_agent_chatbot/
├── app.py                 # Main Streamlit application
├── agents/
│   ├── __init__.py
│   ├── web_search_agent.py
│   ├── sql_agent.py
│   ├── document_agent.py
│   └── router_agent.py
├── config/
│   └── settings.py        # Configuration management
├── utils/
│   ├── __init__.py
│   └── memory.py          # Simple conversation memory
├── data/
│   ├── sample_database.sqlite
│   └── documents/
└── requirements.txt
```

### Step 2: Individual Agent Implementation

#### 2.1 Web Search Agent (`agents/web_search_agent.py`)
```python
class WebSearchAgent:
    def __init__(self, api_key, openai_client):
        self.api_key = api_key
        self.client = openai_client
    
    def search(self, query: str) -> str:
        # Simple web search implementation
        # Return formatted results
    
    def process_query(self, query: str) -> dict:
        # Main processing method
        # Returns: {"response": str, "sources": list, "agent": "web_search"}
```

#### 2.2 SQL Agent (`agents/sql_agent.py`)
```python
class SQLAgent:
    def __init__(self, db_path: str, openai_client):
        self.db_path = db_path
        self.client = openai_client
    
    def get_schema(self) -> str:
        # Return database schema description
    
    def text_to_sql(self, query: str) -> str:
        # Convert natural language to SQL
    
    def execute_sql(self, sql: str) -> pd.DataFrame:
        # Execute SQL safely
    
    def process_query(self, query: str) -> dict:
        # Main processing method
        # Returns: {"response": str, "data": df, "sql": str, "agent": "sql"}
```

#### 2.3 Document Agent (`agents/document_agent.py`)
```python
class DocumentAgent:
    def __init__(self, documents_path: str, openai_client, embedding_client):
        self.documents_path = documents_path
        self.client = openai_client
        self.index = None  # LlamaIndex vector index
    
    def load_documents(self):
        # Load and index documents
    
    def process_query(self, query: str) -> dict:
        # Main processing method
        # Returns: {"response": str, "sources": list, "agent": "document"}
```

#### 2.4 Router Agent (`agents/router_agent.py`)
```python
class RouterAgent:
    def __init__(self, openai_client):
        self.client = openai_client
        self.agents = {}
    
    def register_agent(self, name: str, agent):
        # Register an agent
    
    def route_query(self, query: str) -> str:
        # Determine which agent should handle the query
        # Returns: agent_name ("web_search", "sql", "document")
    
    def process_query(self, query: str) -> dict:
        # Route to appropriate agent and return response
```

### Step 3: Main Streamlit Application (`app.py`)

#### 3.1 Core Features
- Simple chat interface with input box and message history
- Memory system to store conversation history
- Display different response types (text, tables, sources)
- Simple routing logic display

#### 3.2 Memory Implementation
```python
class ConversationMemory:
    def __init__(self):
        self.messages = []
    
    def add_message(self, role: str, content: str, metadata=None):
        # Add message to memory
    
    def get_history(self) -> list:
        # Return conversation history
    
    def clear(self):
        # Clear conversation history
```

#### 3.3 Streamlit Interface
```python
def main():
    st.title("Multi-Agent Chatbot")
    
    # Initialize agents and memory
    memory = ConversationMemory()
    router = RouterAgent(client)
    
    # Register agents
    router.register_agent("web_search", WebSearchAgent(...))
    router.register_agent("sql", SQLAgent(...))
    router.register_agent("document", DocumentAgent(...))
    
    # Chat interface
    user_input = st.text_input("Ask me anything...")
    
    if user_input:
        # Process query
        response = router.process_query(user_input)
        
        # Display response based on agent type
        display_response(response)
        
        # Update memory
        memory.add_message("user", user_input)
        memory.add_message("assistant", response["response"], response)
    
    # Display conversation history
    display_conversation_history(memory.get_history())
```

### Step 4: Configuration Management (`config/settings.py`)
```python
class Settings:
    def __init__(self):
        self.load_env_variables()
    
    def load_env_variables(self):
        # Load all necessary API keys and configurations
        self.openai_key = os.getenv("AZURE_OPENAI_KEY")
        self.brave_search_key = os.getenv("BRAVE_SEARCH_API_KEY")
        # ... other configurations
```

## Implementation Simplifications

### 1. Routing Logic
- Use simple keyword matching initially
- Keywords for web search: "current", "latest", "news", "today", "weather"
- Keywords for SQL: "data", "customers", "orders", "products", "sales", "count", "total"
- Keywords for documents: "document", "explain", "definition", "concept", "summary"
- Default to web search if unclear

### 2. Memory System
- Simple list-based memory (no persistence)
- Store last 20 messages
- Display in chronological order

### 3. Response Display
- Text responses: Simple markdown display
- SQL responses: Show SQL query + results table
- Web search: Show response + source links
- Document responses: Show response + source documents

### 4. Error Handling
- Basic try/catch blocks
- User-friendly error messages
- Fallback to general responses

## Development Steps

### Phase 1: Basic Structure
1. Create project structure
2. Implement basic RouterAgent with keyword matching
3. Create simple Streamlit interface
4. Test routing logic

### Phase 2: Web Search Agent
1. Implement WebSearchAgent using Brave Search API
2. Test integration with router
3. Add to Streamlit interface

### Phase 3: SQL Agent
1. Implement SQLAgent with database connection
2. Add schema understanding
3. Test SQL generation and execution
4. Integrate with interface

### Phase 4: Document Agent
1. Implement DocumentAgent with LlamaIndex
2. Set up document indexing
3. Test document querying
4. Integrate with interface

### Phase 5: Memory & Polish
1. Add conversation memory
2. Improve response display
3. Add error handling
4. Test full system

## Key Decisions

### Simplicity First
- No complex conversation flows
- No session management
- Basic routing without ML
- Simple memory without persistence

### Technology Stack
- Streamlit for web interface
- OpenAI for LLM capabilities
- LlamaIndex for document processing
- SQLite for database queries
- Brave Search for web access

### File Organization
- One agent per file
- Clear separation of concerns
- Minimal dependencies between components
- Easy to extend and modify

## Expected Outcomes

### User Experience
1. User types query
2. System shows which agent is handling it
3. Response displayed with appropriate formatting
4. Conversation history maintained
5. Clear source attribution

### Example Interactions
1. "What's the weather today?" → Web Search Agent
2. "How many customers do we have?" → SQL Agent  
3. "Explain the concept in document 1" → Document Agent
4. "Compare sales data with market trends" → Router decides based on keywords

This plan provides a clear roadmap for implementing a simple but functional multi-agent chatbot system for learning purposes.
