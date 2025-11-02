# Step-by-Step Guide: Adding a New Agent to the AI Analyst System

## Overview
This guide demonstrates how to add a new agent (e.g., **RAG Document Agent**) to the existing multi-agent system. We'll use a document retrieval agent as an example that searches through internal documentation using ChromaDB vector database.

---

## 🎯 Example Agent: Document RAG Agent

**Purpose:** Retrieve information from internal company documents, policies, and knowledge base.

**Use Cases:**
- "What is our company's refund policy?"
- "Find information about employee benefits"
- "Search our documentation for API integration guides"

---

## 📋 Prerequisites

Before adding a new agent, ensure you have:
- ✅ Basic understanding of your existing agent architecture
- ✅ Access to all relevant code files
- ✅ MLflow setup for tracing
- ✅ OpenAI API key configured
- ✅ (For RAG) ChromaDB installed and vector index created

---

## 🔢 Step-by-Step Implementation

### **Step 1: Define Agent Tools** 
📁 File: `app/tools/tools_definitions.py`

Add the tool definition for your new agent using the **new OpenAI schema format**.

```python
def tools_definitions():
    """
    Define all available tools for agents.
    Updated for new OpenAI API format (no nested 'function' key).
    """
    return [
        # Existing tools...
        {
            "type": "function",
            "name": "tool_document_search",  # New tool name
            "description": "Search internal company documents, policies, and knowledge base for relevant information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or question to find relevant documents"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of top results to return (default: 5)",
                        "default": 5
                    },
                    "filter_category": {
                        "type": "string",
                        "description": "Optional category filter (e.g., 'policies', 'technical_docs', 'HR')",
                        "enum": ["policies", "technical_docs", "HR", "finance", "all"]
                    }
                },
                "required": ["query"]
            }
        },
        # ... other existing tools
    ]
```

**Key Points:**
- Use descriptive `name` and `description`
- Define clear parameter schema
- Specify required vs. optional parameters
- Use `enum` for predefined choices

---

### **Step 2: Update MLflow Logging Configuration**
📁 File: `app/config/mlflow_config.py` (or wherever MLflow is configured)

Add logging capabilities for the new agent.

```python
import mlflow
from mlflow.entities import SpanType

# Enable autologging for OpenAI
mlflow.openai.autolog()

# Configure experiment
EXPERIMENT_NAME = "ai-analyst-agent"
mlflow.set_experiment(EXPERIMENT_NAME)

# Agent-specific tags
AGENT_TAGS = {
    "sql_agent": "text2sql_analysis",
    "chart_agent": "visualization_generation",
    "table_router": "table_metadata_retrieval",
    "document_rag_agent": "document_search_rag",  # New agent tag
    "router": "query_routing"
}

def log_agent_execution(agent_name: str, input_data: dict, output_data: dict, metadata: dict = None):
    """
    Log agent execution to MLflow
    """
    with mlflow.start_span(name=agent_name, span_type=SpanType.AGENT) as span:
        span.set_inputs(input_data)
        span.set_outputs(output_data)
        if metadata:
            span.set_attributes(metadata)
```

---

### **Step 3: Update Logging Service**
📁 File: `app/services/logging_service.py`

Add logging methods specific to the new agent.

```python
class LoggingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # ... existing initialization
    
    # Existing methods...
    
    def log_document_search_request(self, query: str, filters: dict = None):
        """Log document search request"""
        self.logger.info(f"Document Search Request: {query}")
        if filters:
            self.logger.info(f"Applied Filters: {filters}")
        
        # MLflow logging
        mlflow.log_param("document_search_query", query)
        if filters:
            mlflow.log_param("document_search_filters", str(filters))
    
    def log_document_search_response(self, results: list, num_results: int):
        """Log document search results"""
        self.logger.info(f"Document Search returned {num_results} results")
        
        # Log to MLflow
        mlflow.log_metric("num_documents_retrieved", num_results)
        
        # Log metadata about sources
        if results:
            sources = [r.get('source', 'unknown') for r in results]
            mlflow.log_param("document_sources", str(sources))
    
    def log_rag_retrieval_metrics(self, relevance_scores: list):
        """Log RAG-specific metrics"""
        if relevance_scores:
            avg_score = sum(relevance_scores) / len(relevance_scores)
            max_score = max(relevance_scores)
            min_score = min(relevance_scores)
            
            mlflow.log_metric("avg_relevance_score", avg_score)
            mlflow.log_metric("max_relevance_score", max_score)
            mlflow.log_metric("min_relevance_score", min_score)
```

**Key Points:**
- Add request logging
- Add response logging
- Log agent-specific metrics
- Include relevant metadata

---

### **Step 4: Create ChromaDB Vector Index** (For RAG Agents)
📁 File: `scripts/create_document_index.py`

Use the pattern from your `rag_llamaindex.ipynb` notebook.

```python
"""
Script to create ChromaDB vector index for document RAG agent.
Based on patterns from notebooks/rag_llamaindex.ipynb
"""

import os
from dotenv import load_dotenv
import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI as LlamaIndexOpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Configure LlamaIndex Settings
llm = LlamaIndexOpenAI(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
embedding_model = OpenAIEmbedding(
    model=OPENAI_EMBEDDING_MODEL,
    api_key=OPENAI_API_KEY,
    api_base="https://api.openai.com/v1"
)

Settings.llm = llm
Settings.embed_model = embedding_model

def create_document_index():
    """
    Create vector index from company documents
    """
    # Define document paths
    doc_paths = [
        "./documents/company_policies.pdf",
        "./documents/employee_handbook.pdf",
        "./documents/technical_guides.md",
        # Add more documents...
    ]
    
    # Define metadata for each document
    def get_metadata_for_files(file_paths):
        file_metadata_map = {
            "./documents/company_policies.pdf": {
                "category": "policies",
                "department": "HR",
                "confidentiality": "internal",
                "last_updated": "2024-10-01"
            },
            "./documents/employee_handbook.pdf": {
                "category": "HR",
                "department": "HR",
                "confidentiality": "public",
                "last_updated": "2024-09-15"
            },
            # Add more metadata...
        }
        
        def file_metadata_func(file_path):
            return file_metadata_map.get(file_path, {
                "source": file_path,
                "category": "unknown"
            })
        
        return file_metadata_func
    
    # Load documents with metadata
    documents = SimpleDirectoryReader(
        input_files=doc_paths,
        file_metadata=get_metadata_for_files(doc_paths)
    ).load_data()
    
    print(f"Loaded {len(documents)} documents")
    
    # Initialize ChromaDB
    index_path = "./index/document_chroma_db"
    db = chromadb.PersistentClient(path=index_path)
    
    # Create collection
    chroma_collection = db.get_or_create_collection("company_documents")
    
    # Create vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create and persist index
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    
    print(f"✅ Index created successfully at {index_path}")
    print(f"Collection: {chroma_collection.name}")
    print(f"Total items: {chroma_collection.count()}")
    
    return index

if __name__ == "__main__":
    create_document_index()
```

**Run this script once to create the index:**
```bash
python scripts/create_document_index.py
```

---

### **Step 5: Implement Agent Function**
📁 File: `agents/agents.py`

Add the new agent function following the existing pattern.

```python
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

# ... existing imports ...

@mlflow.trace(span_type=SpanType.AGENT)
def agent_document_search(user_query: str, top_k: int = 5, filter_category: str = "all"):
    """
    Document RAG agent - searches internal company documents.
    
    Args:
        user_query: User's search query
        top_k: Number of results to return
        filter_category: Optional category filter
        
    Returns:
        str: Retrieved information from documents
    """
    try:
        # Load ChromaDB index
        index_path = "./index/document_chroma_db"
        db = chromadb.PersistentClient(path=index_path)
        chroma_collection = db.get_collection("company_documents")
        
        # Create vector store and index
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context
        )
        
        # Create query engine
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        
        # Build search query
        search_prompt = f"Search for: {user_query}"
        if filter_category != "all":
            search_prompt += f"\nFilter by category: {filter_category}"
        
        # Execute search
        response = query_engine.query(search_prompt)
        
        # Format response with sources
        formatted_response = str(response)
        
        # Add source attribution
        if hasattr(response, 'source_nodes') and response.source_nodes:
            formatted_response += "\n\nSources:\n"
            for i, node in enumerate(response.source_nodes[:3], 1):
                metadata = node.node.metadata
                formatted_response += f"{i}. {metadata.get('source', 'Unknown')} "
                formatted_response += f"(Category: {metadata.get('category', 'N/A')})\n"
        
        return formatted_response
        
    except Exception as e:
        error_msg = f"Error in document search: {str(e)}"
        print(error_msg)
        return f"I encountered an error searching the documents: {str(e)}"


# Export the new agent
__all__ = [
    'routing_agent',
    'agent_sql_analysis',
    'agent_generate_charts',
    'agent_table_router',
    'agent_final_response',
    'agent_document_search'  # Add new agent
]
```

**Key Points:**
- Use `@mlflow.trace` decorator for observability
- Handle errors gracefully
- Return formatted, user-friendly responses
- Include source attribution

---

### **Step 6: Create Agent Prompt**
📁 File: `app/prompts/prompt_agent_document_search.py`

Define the system prompt for your new agent.

```python
def prompt_agent_document_search():
    return """
# Agent: Document Search (RAG)

You are a specialized document search agent that retrieves information from internal company documents, policies, and knowledge bases.

## Your Capabilities:
1. Search through company documentation using semantic similarity
2. Retrieve relevant passages from policies, handbooks, and technical guides
3. Provide accurate, citation-backed answers
4. Filter by document category when needed

## Your Process:
1. **Understand the query**: Identify what information the user needs
2. **Search documents**: Use semantic search to find relevant passages
3. **Synthesize information**: Combine information from multiple sources if needed
4. **Cite sources**: Always reference which documents you're pulling from
5. **Provide context**: Give clear, actionable answers

## Guidelines:
- **Be precise**: Only answer based on retrieved document content
- **Cite sources**: Always mention which document(s) you're referencing
- **Admit limitations**: If information isn't in the documents, say so clearly
- **Stay current**: Note if documents have timestamps or version info
- **Be helpful**: Suggest related topics if relevant

## Response Format:
1. Direct answer to the user's question
2. Supporting details from documents
3. Source citations (document name, category, section if available)
4. Related information (if applicable)

## Example Responses:

**Query:** "What is our remote work policy?"

**Response:**
Based on our Employee Handbook (last updated Oct 2024), our remote work policy allows:

1. **Eligibility**: All full-time employees after 90-day probation
2. **Frequency**: Up to 3 days per week (manager approval required)
3. **Requirements**: 
   - Stable internet connection (min 25 Mbps)
   - Dedicated workspace
   - Available during core hours (10 AM - 3 PM local time)

**Source:** Employee Handbook, Section 4.2 - Remote Work Guidelines

Related: See also "Equipment Reimbursement Policy" for home office setup allowances.

---

## Error Handling:
- If no relevant documents found: "I couldn't find information about [topic] in our current documentation. You may want to contact [relevant department] directly."
- If query is too vague: "Could you please be more specific about [aspect]? This will help me search our documentation more effectively."
- If information is outdated: "The most recent information I have is from [date]. Please verify with [department] for the latest updates."

## Security & Compliance:
- Only return information from documents you have access to
- Respect confidentiality levels in document metadata
- Never fabricate information not present in documents
- Flag if query requests sensitive/restricted information

Remember: Your role is to be a reliable bridge between users and company documentation. Accuracy and proper citation are paramount.
"""
```

**Also update the prompts `__init__.py`:**

📁 File: `app/prompts/__init__.py`

```python
from .prompt_agent_router import prompt_agent_router
from .prompt_agent_sql_analysis import prompt_agent_sql_analysis
from .prompt_agent_final_response import prompt_agent_final_response
from .prompt_agent_plot import prompt_agent_plot
from .prompt_agent_table_router import prompt_agent_table_router
from .prompt_agent_document_search import prompt_agent_document_search  # New

__all__ = [
    'prompt_agent_router',
    'prompt_agent_sql_analysis',
    'prompt_agent_final_response',
    'prompt_agent_plot',
    'prompt_agent_table_router',
    'prompt_agent_document_search'  # New
]
```

---

### **Step 7: Update Core Text2SQL Engine**
📁 File: `app/core/text2sql_engine.py`

Integrate the new agent into the main processing pipeline.

```python
# Add import at the top
from agents.agents import (
    routing_agent,
    agent_sql_analysis,
    agent_generate_charts,
    agent_table_router,
    agent_final_response,
    agent_document_search  # New import
)

class Text2SQLEngine:
    # ... existing code ...
    
    async def process_query(self, user_input: str, chat_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Main processing pipeline with new document search agent
        """
        if chat_history is None:
            chat_history = []
        
        if not chat_history or chat_history[-1]["role"] != "user":
            chat_history.append({"role": "user", "content": user_input})
        
        self.logging_service.start_chat_run(user_input)
        
        try:
            # Step 1: Route the query
            router_response = routing_agent(user_input, chat_history)
            
            sql_results = []
            chart_results = []
            document_results = []  # New result container
            
            # Step 2: Process tool calls
            if router_response.output:
                for item in router_response.output:
                    if item.type == "function_call":
                        function_name = item.name
                        function_args = json.loads(item.arguments)
                        
                        # Handle SQL analysis
                        if function_name == "tool_sql_analysis":
                            sql_results, chart_html, _ = await self._handle_sql_analysis(
                                user_input, function_args, agent_sql_analysis,
                                agent_table_router, execute_sql_with_pyodbc,
                                agent_generate_charts, execute_plot_code
                            )
                        
                        # Handle document search (NEW)
                        elif function_name == "tool_document_search":
                            document_results = await self._handle_document_search(
                                function_args, agent_document_search
                            )
            
            # Step 3: Generate final response
            polish_prompt = self._build_polish_prompt_with_documents(
                sql_results, chart_results, document_results, user_input
            )
            
            if polish_prompt:
                final_response_text = agent_final_response(polish_prompt, chat_history)
            else:
                final_response_text = self._create_fallback_message(
                    sql_results, chart_results, document_results
                )
            
            return {
                "response": final_response_text,
                "sql_results": sql_results,
                "chart_results": chart_results,
                "document_results": document_results,  # New
                "chart_html": chart_html
            }
            
        except Exception as e:
            self.logging_service.log_error(str(e))
            raise
        finally:
            self.logging_service.end_chat_run()
    
    async def _handle_document_search(self, function_args: dict, 
                                      agent_document_search) -> List[Dict[str, Any]]:
        """
        Handle document search requests (NEW METHOD)
        """
        results = []
        try:
            query = function_args.get("query", "")
            top_k = function_args.get("top_k", 5)
            filter_category = function_args.get("filter_category", "all")
            
            # Log request
            self.logging_service.log_document_search_request(
                query, {"top_k": top_k, "filter_category": filter_category}
            )
            
            # Execute document search
            search_response = agent_document_search(query, top_k, filter_category)
            
            # Log response
            self.logging_service.log_document_search_response([search_response], 1)
            
            results.append({
                "type": "document_success",
                "query": query,
                "response": search_response,
                "category": filter_category
            })
            
        except Exception as e:
            self.logging_service.log_error(f"Document search error: {str(e)}")
            results.append({
                "type": "document_error",
                "query": function_args.get("query", ""),
                "error": str(e)
            })
        
        return results
    
    def _build_polish_prompt_with_documents(self, sql_results: List[Dict], 
                                           chart_results: List[Dict],
                                           document_results: List[Dict],
                                           user_input: str) -> Optional[str]:
        """
        Updated polish prompt builder that includes document results
        """
        if not sql_results and not chart_results and not document_results:
            return None
        
        prompt_parts = [f"User Query: '{user_input}'\n"]
        
        # SQL results
        successful_sql = [r for r in sql_results if r["type"] == "sql_success"]
        if successful_sql:
            prompt_parts.append("SQL Query Results:")
            for result in successful_sql:
                prompt_parts.append(f"- {result}")
        
        # Chart results
        successful_charts = [r for r in chart_results if r["type"] == "chart_success"]
        if successful_charts:
            prompt_parts.append("\nVisualization Results:")
            for result in successful_charts:
                prompt_parts.append(f"- {result}")
        
        # Document results (NEW)
        successful_docs = [r for r in document_results if r["type"] == "document_success"]
        if successful_docs:
            prompt_parts.append("\nDocument Search Results:")
            for result in successful_docs:
                prompt_parts.append(f"- Query: {result['query']}")
                prompt_parts.append(f"  Response: {result['response']}")
        
        prompt_parts.append("\nPlease provide a clear, friendly summary of these results.")
        
        return "\n".join(prompt_parts)
```

---

### **Step 8: Update Router Agent Prompt**
📁 File: `app/prompts/prompt_agent_router.py`

Update the router to be aware of the new agent (see separate file `ROUTER_PROMPT_WITH_NEW_AGENT.md`).

---

### **Step 9: Test the New Agent**

Create a test script to verify everything works.

📁 File: `tests/test_document_agent.py`

```python
"""
Test script for document search agent
"""
import asyncio
from app.core.text2sql_engine import Text2SQLEngine
from app.services.logging_service import LoggingService
from app.services.openai_service import OpenAIService
from app.services.database_service import DatabaseService
from app.services.vector_service import VectorService

async def test_document_agent():
    # Initialize services
    services = {
        'openai': OpenAIService(),
        'database': DatabaseService(),
        'vector': VectorService(),
        'logging': LoggingService()
    }
    
    # Create engine
    engine = Text2SQLEngine(services)
    
    # Test queries
    test_queries = [
        "What is our company's remote work policy?",
        "Find information about employee benefits",
        "Search for API integration documentation"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing: {query}")
        print('='*60)
        
        result = await engine.process_query(query)
        
        print(f"\nResponse: {result['response']}")
        if result.get('document_results'):
            print(f"\nDocument Results: {len(result['document_results'])}")

if __name__ == "__main__":
    asyncio.run(test_document_agent())
```

**Run the test:**
```bash
python tests/test_document_agent.py
```

---

### **Step 10: Verify MLflow Tracing**

1. Start MLflow UI:
```bash
mlflow ui --port 5000
```

2. Navigate to http://localhost:5000

3. Check for:
   - ✅ `agent_document_search` spans
   - ✅ Correct input/output logging
   - ✅ Timing metrics
   - ✅ Error tracking (if any)

---

## 🎉 Completion Checklist

After following all steps, verify:

- [ ] Tool definition added to `tools_definitions.py`
- [ ] MLflow configuration updated
- [ ] Logging service has new methods
- [ ] ChromaDB vector index created (for RAG agents)
- [ ] Agent function implemented in `agents.py`
- [ ] Agent prompt created
- [ ] Core engine updated to handle new agent
- [ ] Router prompt updated
- [ ] Test script created and passing
- [ ] MLflow traces visible in UI
- [ ] Documentation updated

---

## 📊 Testing & Validation

### Unit Tests
```python
# Test agent in isolation
from agents.agents import agent_document_search

result = agent_document_search("test query", top_k=3)
assert result is not None
assert isinstance(result, str)
```

### Integration Tests
```python
# Test full pipeline
result = await engine.process_query("What is our refund policy?")
assert "document_results" in result
assert result["response"] is not None
```

### MLflow Validation
- Check span hierarchy
- Verify timing metrics
- Confirm error logging
- Review token usage

---

## 🔧 Troubleshooting

### Common Issues

**1. Agent not being called**
- Check router prompt includes new agent
- Verify tool definition is correct
- Ensure function name matches exactly

**2. ChromaDB connection errors**
- Verify index path is correct
- Check collection name matches
- Ensure index was created successfully

**3. MLflow not logging**
- Verify `@mlflow.trace` decorator is present
- Check MLflow is initialized
- Ensure experiment is set

**4. Import errors**
- Check all `__init__.py` files updated
- Verify new modules are in correct location
- Restart kernel/server after changes

---

## 🚀 Next Steps

After successfully adding one agent, you can:

1. **Add more specialized agents** (e.g., web search, calculation, image generation)
2. **Implement agent chaining** (one agent's output feeds another)
3. **Add fallback mechanisms** (if primary agent fails, try secondary)
4. **Implement caching** (store frequent query results)
5. **Add A/B testing** (compare different agent implementations)

---

## 📚 Additional Resources

- [OpenAI Function Calling Docs](https://platform.openai.com/docs/guides/function-calling)
- [LlamaIndex Documentation](https://docs.llamaindex.ai)
- [ChromaDB Guide](https://docs.trychroma.com)
- [MLflow Tracing](https://mlflow.org/docs/latest/llms/tracing)

---

**Prepared for: Scaling Agentic AI Presentation**  
**Date:** November 1, 2025  
**Author:** AI Analyst Team
