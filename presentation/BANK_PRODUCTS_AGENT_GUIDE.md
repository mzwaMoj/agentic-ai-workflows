# Step-by-Step Guide: Adding a Bank Products Agent
## Using RAG with ChromaDB for Product Recommendations

## Overview
This guide demonstrates how to add a **Bank Products Agent** to the existing multi-agent system. This agent uses RAG (Retrieval-Augmented Generation) with ChromaDB to search through bank products and services, helping customers find the right financial products based on their needs, income, credit score, and other criteria.

---

## 🎯 Bank Products Agent

**Purpose:** Retrieve and recommend bank products and services based on customer requirements.

**Use Cases:**
- "I make $45,000 per year and want to open a savings account, what options do I have?"
- "What credit cards are available for someone with a 680 credit score?"
- "I'm a small business owner looking for a business checking account"
- "Find me a mortgage option for first-time homebuyers with $50,000 household income"
- "What auto loan rates do you offer for used cars?"

**Data Source:** `/documents/bank_products_services.txt` (comprehensive product catalog)

---

## 📋 Prerequisites

Before adding the bank products agent, ensure you have:
- ✅ Bank products catalog created (`documents/bank_products_services.txt`)
- ✅ Access to all relevant code files
- ✅ MLflow setup for tracing
- ✅ OpenAI API key configured
- ✅ ChromaDB and LlamaIndex installed

---

## 🔢 Step-by-Step Implementation

### **Step 1: Define Agent Tools** 
📁 File: `app/tools/tools_definitions.py`

Add the tool definition for the bank products agent using the **new OpenAI schema format**.

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
            "name": "tool_bank_products",
            "description": "Search bank products and services catalog to find suitable financial products based on customer criteria such as income, credit score, age, employment status, and product type. Returns detailed product information including eligibility, features, rates, and fees.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query describing what the customer is looking for. Include relevant criteria like income, credit score, purpose, etc."
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of most relevant products to retrieve",
                        "default": 5
                    },
                    "product_category": {
                        "type": "string",
                        "enum": [
                            "all",
                            "savings_accounts",
                            "checking_accounts", 
                            "credit_cards",
                            "personal_loans",
                            "home_loans",
                            "auto_loans",
                            "business_accounts",
                            "investment_products",
                            "specialty_accounts"
                        ],
                        "description": "Filter by specific product category",
                        "default": "all"
                    },
                    "income_range": {
                        "type": "string",
                        "description": "Customer's annual income (e.g., '$45,000', 'under $30k', '$50k-$75k')",
                        "default": null
                    },
                    "credit_score": {
                        "type": "integer",
                        "description": "Customer's credit score (300-850)",
                        "default": null
                    }
                },
                "required": ["query"]
            }
        }
    ]
```

**Key Points:**
- Tool name: `tool_bank_products`
- Allows filtering by product category, income, and credit score
- Uses natural language queries for flexible search
- Returns top K most relevant products

---

### **Step 2: Update MLflow Configuration**
📁 File: `app/config/mlflow_config.py`

Add tracking configuration for the bank products agent.

```python
# Agent names for MLflow tracking
AGENT_TAGS = {
    "router": "router_agent",
    "sql": "sql_analysis_agent",
    "chart": "chart_generation_agent",
    "table": "table_router_agent",
    "final": "final_response_agent",
    "products": "bank_products_agent"  # NEW
}

# Span types for different operations
SPAN_TYPES = {
    "agent": SpanType.AGENT,
    "chain": SpanType.CHAIN,
    "retriever": SpanType.RETRIEVER,  # Important for RAG
    "tool": SpanType.TOOL,
    "llm": SpanType.LLM
}

def log_agent_execution(agent_name, input_data, output_data, metadata=None):
    """
    Log agent execution to MLflow with proper span type.
    """
    with mlflow.start_span(
        name=f"{agent_name}_execution",
        span_type=SPAN_TYPES["agent"]
    ) as span:
        span.set_inputs(input_data)
        span.set_outputs(output_data)
        if metadata:
            span.set_attributes(metadata)
```

---

### **Step 3: Update Logging Service**
📁 File: `app/services/logging_service.py`

Add logging methods specific to the bank products agent.

```python
import mlflow
from mlflow.entities import SpanType

class LoggingService:
    # Existing methods...
    
    @staticmethod
    @mlflow.trace(name="bank_products_request", span_type=SpanType.AGENT)
    def log_bank_products_request(query, filters, top_k):
        """
        Log bank products search request.
        """
        return {
            "query": query,
            "filters": filters,
            "top_k": top_k,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    @mlflow.trace(name="bank_products_response", span_type=SpanType.AGENT)
    def log_bank_products_response(products_found, num_results, query_time):
        """
        Log bank products search response.
        """
        return {
            "num_results": num_results,
            "products": [p["product_code"] for p in products_found],
            "query_time_ms": query_time,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    @mlflow.trace(name="rag_retrieval", span_type=SpanType.RETRIEVER)
    def log_rag_retrieval_metrics(query, retrieved_docs, similarity_scores, retrieval_time):
        """
        Log RAG retrieval metrics for observability.
        """
        return {
            "query": query,
            "num_docs_retrieved": len(retrieved_docs),
            "avg_similarity_score": sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0,
            "min_similarity": min(similarity_scores) if similarity_scores else 0,
            "max_similarity": max(similarity_scores) if similarity_scores else 0,
            "retrieval_time_ms": retrieval_time,
            "doc_ids": [doc.doc_id for doc in retrieved_docs],
            "timestamp": datetime.now().isoformat()
        }
```

**Key Points:**
- Use `SpanType.AGENT` for agent-level operations
- Use `SpanType.RETRIEVER` for RAG retrieval operations
- Log both requests and responses for full traceability
- Track performance metrics (query time, similarity scores)

---

### **Step 4: Create ChromaDB Vector Index**
📁 File: `scripts/create_products_index.py`

Create a script to index the bank products catalog using LlamaIndex and ChromaDB.

```python
"""
Create ChromaDB vector index for bank products catalog.
Run this script once to create the index, then use it in the agent.
"""

import os
import chromadb
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()

def create_products_index():
    """
    Create ChromaDB vector index from bank products catalog.
    """
    print("🚀 Creating Bank Products Vector Index...")
    
    # Step 1: Load products catalog
    products_file = "documents/bank_products_services.txt"
    
    if not os.path.exists(products_file):
        raise FileNotFoundError(f"Products catalog not found: {products_file}")
    
    with open(products_file, 'r', encoding='utf-8') as f:
        products_text = f.read()
    
    print(f"✅ Loaded products catalog ({len(products_text)} characters)")
    
    # Step 2: Create documents with metadata
    # Split by product sections (identified by "### ")
    product_sections = []
    current_section = []
    current_title = ""
    
    for line in products_text.split('\n'):
        if line.startswith('### '):
            # Save previous section
            if current_section:
                product_sections.append({
                    'title': current_title,
                    'content': '\n'.join(current_section)
                })
            # Start new section
            current_title = line.replace('### ', '').strip()
            current_section = [line]
        elif line.startswith('## ') and 'Product Code:' not in line:
            # Category header
            if current_section:
                product_sections.append({
                    'title': current_title or 'Introduction',
                    'content': '\n'.join(current_section)
                })
            current_title = line.replace('## ', '').strip()
            current_section = [line]
        else:
            current_section.append(line)
    
    # Add last section
    if current_section:
        product_sections.append({
            'title': current_title,
            'content': '\n'.join(current_section)
        })
    
    print(f"✅ Split into {len(product_sections)} product sections")
    
    # Step 3: Create LlamaIndex documents with metadata
    documents = []
    for idx, section in enumerate(product_sections):
        # Extract metadata from content
        content = section['content']
        metadata = {
            'source': 'bank_products_catalog',
            'section_title': section['title'],
            'section_id': idx
        }
        
        # Extract product code if present
        if 'Product Code:' in content:
            for line in content.split('\n'):
                if 'Product Code:' in line:
                    product_code = line.split('Product Code:')[1].strip().replace('**', '')
                    metadata['product_code'] = product_code
                    break
        
        # Categorize by section title
        title_lower = section['title'].lower()
        if 'savings' in title_lower:
            metadata['category'] = 'savings_accounts'
        elif 'checking' in title_lower:
            metadata['category'] = 'checking_accounts'
        elif 'credit card' in title_lower:
            metadata['category'] = 'credit_cards'
        elif 'personal loan' in title_lower:
            metadata['category'] = 'personal_loans'
        elif 'mortgage' in title_lower or 'home' in title_lower:
            metadata['category'] = 'home_loans'
        elif 'auto' in title_lower or 'car' in title_lower:
            metadata['category'] = 'auto_loans'
        elif 'business' in title_lower:
            metadata['category'] = 'business_accounts'
        elif 'cd' in title_lower or 'money market' in title_lower or 'investment' in title_lower:
            metadata['category'] = 'investment_products'
        elif 'hsa' in title_lower or '529' in title_lower:
            metadata['category'] = 'specialty_accounts'
        else:
            metadata['category'] = 'general_info'
        
        doc = Document(
            text=content,
            metadata=metadata,
            id_=f"product_{idx}"
        )
        documents.append(doc)
    
    print(f"✅ Created {len(documents)} documents with metadata")
    
    # Step 4: Initialize ChromaDB
    chroma_client = chromadb.PersistentClient(path="./index/chroma_products_db")
    
    # Delete existing collection if it exists
    try:
        chroma_client.delete_collection("bank_products")
        print("🗑️  Deleted existing collection")
    except:
        pass
    
    chroma_collection = chroma_client.create_collection("bank_products")
    
    # Step 5: Create vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Step 6: Initialize embedding model
    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Step 7: Create index with smaller chunk sizes for better retrieval
    node_parser = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=50
    )
    
    print("🔨 Building vector index...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        transformations=[node_parser],
        show_progress=True
    )
    
    print("✅ Vector index created successfully!")
    print(f"📊 Index stats:")
    print(f"   - Total documents: {len(documents)}")
    print(f"   - Storage path: ./index/chroma_products_db")
    print(f"   - Collection name: bank_products")
    print(f"   - Embedding model: text-embedding-3-small")
    
    return index

if __name__ == "__main__":
    create_products_index()
    print("\n🎉 Bank Products Index creation complete!")
    print("💡 You can now use this index in the bank_products_agent")
```

**Run this script:**
```bash
cd /path/to/ai-analyst-agent
python scripts/create_products_index.py
```

**Key Points:**
- Uses `text-embedding-3-small` for cost-effective embeddings
- Chunks products into semantic sections
- Adds metadata (product_code, category, section_title) for filtering
- Stores in persistent ChromaDB at `./index/chroma_products_db`

---

### **Step 5: Implement Bank Products Agent**
📁 File: `agents/agents.py`

Add the agent function that performs RAG retrieval and product recommendations.

```python
import mlflow
from mlflow.entities import SpanType
import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
import os
import time

@mlflow.trace(name="bank_products_agent", span_type=SpanType.AGENT)
def agent_bank_products(
    query: str,
    top_k: int = 5,
    product_category: str = "all",
    income_range: str = None,
    credit_score: int = None
) -> dict:
    """
    Bank Products Agent: Search and recommend bank products using RAG.
    
    Args:
        query: Natural language query describing customer needs
        top_k: Number of products to retrieve
        product_category: Filter by product category
        income_range: Customer's income range
        credit_score: Customer's credit score
        
    Returns:
        Dict containing recommended products and explanations
    """
    from app.services.logging_service import LoggingService
    
    start_time = time.time()
    
    # Log request
    LoggingService.log_bank_products_request(
        query=query,
        filters={
            "category": product_category,
            "income": income_range,
            "credit_score": credit_score
        },
        top_k=top_k
    )
    
    try:
        # Step 1: Initialize ChromaDB and load index
        chroma_client = chromadb.PersistentClient(path="./index/chroma_products_db")
        chroma_collection = chroma_client.get_collection("bank_products")
        
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        # Step 2: Initialize embedding model
        embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Step 3: Load index
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=embed_model
        )
        
        # Step 4: Enhance query with customer criteria
        enhanced_query = query
        
        if income_range:
            enhanced_query += f" Customer income: {income_range}."
        
        if credit_score:
            enhanced_query += f" Customer credit score: {credit_score}."
        
        if product_category and product_category != "all":
            enhanced_query += f" Looking specifically for {product_category.replace('_', ' ')}."
        
        # Step 5: Build query engine with filters
        filters = {}
        if product_category and product_category != "all":
            filters["category"] = product_category
        
        query_engine = index.as_query_engine(
            similarity_top_k=top_k,
            filters=filters if filters else None
        )
        
        # Step 6: Retrieve relevant products
        retrieval_start = time.time()
        response = query_engine.query(enhanced_query)
        retrieval_time = (time.time() - retrieval_start) * 1000
        
        # Step 7: Extract retrieved documents and scores
        retrieved_docs = []
        similarity_scores = []
        
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                retrieved_docs.append(node)
                similarity_scores.append(node.score if hasattr(node, 'score') else 0.0)
        
        # Log retrieval metrics
        LoggingService.log_rag_retrieval_metrics(
            query=enhanced_query,
            retrieved_docs=retrieved_docs,
            similarity_scores=similarity_scores,
            retrieval_time=retrieval_time
        )
        
        # Step 8: Format products for response
        products_found = []
        for node in retrieved_docs:
            product_info = {
                "product_code": node.metadata.get('product_code', 'N/A'),
                "section_title": node.metadata.get('section_title', 'Unknown'),
                "category": node.metadata.get('category', 'general'),
                "relevance_score": round(node.score if hasattr(node, 'score') else 0.0, 3),
                "content": node.text[:500] + "..." if len(node.text) > 500 else node.text
            }
            products_found.append(product_info)
        
        # Step 9: Generate response
        total_time = (time.time() - start_time) * 1000
        
        # Log response
        LoggingService.log_bank_products_response(
            products_found=products_found,
            num_results=len(products_found),
            query_time=total_time
        )
        
        result = {
            "status": "success",
            "query": query,
            "enhanced_query": enhanced_query,
            "num_products_found": len(products_found),
            "products": products_found,
            "answer": str(response),
            "filters_applied": {
                "category": product_category,
                "income": income_range,
                "credit_score": credit_score
            },
            "performance": {
                "retrieval_time_ms": round(retrieval_time, 2),
                "total_time_ms": round(total_time, 2)
            }
        }
        
        return result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error": str(e),
            "query": query
        }
        mlflow.log_dict(error_result, "bank_products_error.json")
        return error_result
```

**Key Points:**
- Decorated with `@mlflow.trace` for automatic tracing
- Loads ChromaDB index from persistent storage
- Enhances query with customer criteria
- Filters by product category when specified
- Logs retrieval metrics (similarity scores, timing)
- Returns structured product recommendations

---

### **Step 6: Create Agent Prompt**
📁 File: `app/prompts/prompt_agent_bank_products.py`

Create the system prompt for the bank products agent.

```python
def get_bank_products_agent_prompt():
    """
    System prompt for the Bank Products Agent.
    This agent helps customers find suitable bank products based on their needs.
    """
    return """
You are a **Bank Products Specialist Agent** for a retail bank. Your role is to help customers find the most suitable banking products based on their financial situation, needs, and goals.

## Your Responsibilities:

1. **Understand Customer Needs:**
   - Ask clarifying questions if income, credit score, or other criteria are unclear
   - Identify the customer's primary goal (saving, borrowing, investing, business needs)
   - Consider the customer's life stage (student, young professional, family, retiree, business owner)

2. **Product Matching:**
   - Use the retrieved product information from the RAG system
   - Match products to customer eligibility (income, credit score, age, employment)
   - Consider both what the customer qualifies for AND what best serves their needs

3. **Provide Clear Recommendations:**
   - Explain WHY each product is suitable for the customer
   - Highlight key features that match the customer's situation
   - Mention eligibility requirements transparently
   - Compare 2-3 options when multiple products fit
   - Note any special benefits or limitations

4. **Be Transparent About Costs:**
   - Always mention fees, interest rates, and minimum balances
   - Explain any requirements to waive fees
   - Highlight the total cost of ownership

5. **Ethical Guidance:**
   - Never recommend products the customer doesn't qualify for
   - Don't oversell - recommend what's genuinely suitable
   - If no products match, explain why and suggest alternatives
   - Mention when a customer might want to improve their credit or save more before applying

## Response Format:

When answering customer queries:

### Recommended Products:
[List 2-3 most suitable products with Product Code]

### Product 1: [Product Name]
- **Why it's suitable:** [Brief explanation matching their criteria]
- **Key Features:** [2-3 most relevant features]
- **Costs:** [Fees, rates, minimums]
- **Eligibility:** [Requirements they meet]

### Product 2: [Product Name]
[Same format]

### Next Steps:
[What the customer should do to apply or learn more]

### Important Notes:
[Any caveats, alternatives, or suggestions]

---

## Special Considerations:

**For Credit Products (Credit Cards, Loans):**
- Credit score ranges: 300-579 (Poor), 580-669 (Fair), 670-739 (Good), 740-799 (Very Good), 800-850 (Excellent)
- Be realistic about approval odds based on credit score
- Mention credit-building alternatives for those with low scores

**For Savings/Investment Products:**
- Help customers understand tradeoffs (liquidity vs. returns)
- Mention FDIC insurance limits ($250,000)
- Suggest diversification when appropriate

**For Business Products:**
- Consider business age and revenue requirements
- Mention required documentation upfront
- Suggest appropriate products for business stage (startup vs. established)

**For First-Time Customers:**
- Recommend starting with simpler products
- Explain banking basics when helpful
- Suggest product combinations (e.g., checking + savings)

---

## Tone and Style:

- **Helpful and Educational:** Explain concepts customers might not understand
- **Honest and Transparent:** Never hide fees or requirements
- **Concise but Complete:** Provide enough detail without overwhelming
- **Professional yet Friendly:** Be approachable while maintaining expertise

---

## Example Interactions:

**Query:** "I make $45,000 per year and want to open a savings account"

**Your Response:**
Based on your $45,000 annual income, I have two excellent savings account options for you:

### Recommended Products:

**1. Premium Savings Account (SAV-002)**
- **Why it's suitable:** You qualify with your income, and the 4.25% APY will help your money grow significantly faster than basic savings accounts.
- **Key Features:** 
  - High 4.25% APY (8.5x higher than Essential Savings)
  - Unlimited free ATM withdrawals
  - Dedicated customer service
- **Costs:** $15/month fee (waived with $5,000 balance)
- **Eligibility:** ✅ You meet the $30,000 income requirement and 650+ credit score

**2. Essential Savings Account (SAV-001)**
- **Why it's suitable:** If you're just starting to build savings or want minimal requirements
- **Key Features:**
  - Low $25 opening deposit
  - Only $100 minimum balance
  - 0.50% APY
- **Costs:** $5/month fee (waived with $500 balance)
- **Eligibility:** ✅ No income requirements

### My Recommendation:
Start with the **Premium Savings Account** if you can maintain a $5,000 balance (fee waived). The 4.25% interest rate means you'll earn $212.50 per year on a $5,000 balance, compared to just $25 with the Essential account.

If you're building up to $5,000, start with Essential Savings, then upgrade once you hit that threshold.

### Next Steps:
- Open online in 10 minutes with valid ID and initial deposit
- Link to your external bank account for easy transfers
- Set up automatic savings transfers to build balance

---

**Remember:** Always base your recommendations on the retrieved product information. If the RAG system doesn't return relevant products, acknowledge the limitation and suggest the customer speak with a specialist or check the website for more options.

**Current Date:** November 1, 2025
"""
```

**Key Points:**
- Comprehensive guidance for product matching
- Ethical recommendations (don't oversell)
- Structured response format
- Examples of good responses
- Transparency about costs and eligibility

---

### **Step 7: Update Core Engine**
📁 File: `app/core/text2sql_engine.py`

Add handler for bank products agent in the main orchestration engine.

```python
from agents.agents import (
    routing_agent,
    agent_sql_analysis,
    agent_generate_charts,
    agent_table_router,
    agent_final_response,
    agent_bank_products  # NEW IMPORT
)
from app.prompts.prompt_agent_bank_products import get_bank_products_agent_prompt

class Text2SQLEngine:
    # Existing code...
    
    def _handle_bank_products(self, tool_call) -> dict:
        """
        Handle bank products search requests.
        Calls the bank products agent with RAG retrieval.
        """
        try:
            args = json.loads(tool_call.arguments)
            
            query = args.get('query')
            top_k = args.get('top_k', 5)
            product_category = args.get('product_category', 'all')
            income_range = args.get('income_range')
            credit_score = args.get('credit_score')
            
            # Call bank products agent
            products_result = agent_bank_products(
                query=query,
                top_k=top_k,
                product_category=product_category,
                income_range=income_range,
                credit_score=credit_score
            )
            
            if products_result['status'] == 'success':
                # Build polish prompt with product information
                polished_response = self._build_polish_prompt_with_products(
                    user_query=query,
                    products_data=products_result
                )
                
                return {
                    'call_id': tool_call.call_id,
                    'output': polished_response
                }
            else:
                return {
                    'call_id': tool_call.call_id,
                    'output': json.dumps({
                        'error': products_result.get('error', 'Unknown error'),
                        'message': 'Failed to retrieve products'
                    })
                }
                
        except Exception as e:
            return {
                'call_id': tool_call.call_id,
                'output': json.dumps({'error': str(e)})
            }
    
    def _build_polish_prompt_with_products(self, user_query: str, products_data: dict) -> str:
        """
        Build a prompt for the LLM to polish the product recommendations.
        Uses the bank products agent system prompt.
        """
        products_list = products_data.get('products', [])
        
        context = f"""
User Query: {user_query}

Retrieved Products ({products_data['num_products_found']} found):

"""
        
        for idx, product in enumerate(products_list, 1):
            context += f"""
{idx}. {product['section_title']} (Product Code: {product['product_code']})
   Category: {product['category']}
   Relevance: {product['relevance_score']}
   
   {product['content']}

---
"""
        
        # Add filters if applied
        if products_data.get('filters_applied'):
            context += f"\nFilters Applied: {json.dumps(products_data['filters_applied'], indent=2)}\n"
        
        # Add system prompt
        system_prompt = get_bank_products_agent_prompt()
        
        full_prompt = f"""
{system_prompt}

---

{context}

Based on the above retrieved products and the user's query, provide a helpful recommendation following the response format specified in your instructions.
"""
        
        # Get polished response from LLM
        from openai import OpenAI
        import os
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.responses.create(
            model="gpt-4o",
            input=full_prompt
        )
        
        return response.output_text
    
    def process_tool_calls(self, tool_calls):
        """
        Process tool calls from router agent.
        Updated to handle bank products tool.
        """
        tool_outputs = []
        
        for tool_call in tool_calls:
            if tool_call.name == "tool_sql_analysis":
                output = self._handle_sql_analysis(tool_call)
            elif tool_call.name == "tool_generate_chart":
                output = self._handle_chart_generation(tool_call)
            elif tool_call.name == "tool_table_router":
                output = self._handle_table_routing(tool_call)
            elif tool_call.name == "tool_bank_products":  # NEW
                output = self._handle_bank_products(tool_call)
            else:
                output = {
                    'call_id': tool_call.call_id,
                    'output': json.dumps({'error': f'Unknown tool: {tool_call.name}'})
                }
            
            tool_outputs.append(output)
        
        return tool_outputs
```

**Key Points:**
- Add import for `agent_bank_products` and prompt
- Create `_handle_bank_products()` method
- Create `_build_polish_prompt_with_products()` for response formatting
- Update `process_tool_calls()` to route to bank products handler
- Use bank products agent prompt for response generation

---

### **Step 8: Update Router Prompt**
📁 File: `app/prompts/prompt_agent_router.py`

Update router prompt to include bank products agent. See **`BANK_PRODUCTS_ROUTER_PROMPT.md`** for the complete updated prompt.

**Key additions:**
- Add `tool_bank_products` to available tools
- Add routing logic for product/account queries
- Add examples of queries that should use bank products agent
- Update decision tree

---

### **Step 9: Create Test Script**
📁 File: `tests/test_bank_products_agent.py`

Create a test script to verify the bank products agent works correctly.

```python
"""
Test script for Bank Products Agent
Tests RAG retrieval and product recommendations
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from agents.agents import agent_bank_products

def test_savings_account_query():
    """Test: Customer looking for savings account"""
    print("\n" + "="*80)
    print("TEST 1: Savings Account Query")
    print("="*80)
    
    result = agent_bank_products(
        query="I make $45,000 per year and want to open a savings account with good interest rates",
        top_k=3,
        product_category="savings_accounts",
        income_range="$45,000",
        credit_score=None
    )
    
    print(f"\nStatus: {result['status']}")
    print(f"Products Found: {result['num_products_found']}")
    print(f"\nAnswer:\n{result['answer']}")
    
    assert result['status'] == 'success'
    assert result['num_products_found'] > 0

def test_credit_card_query():
    """Test: Customer looking for credit card"""
    print("\n" + "="*80)
    print("TEST 2: Credit Card Query")
    print("="*80)
    
    result = agent_bank_products(
        query="What credit cards are available for someone with a 680 credit score?",
        top_k=3,
        product_category="credit_cards",
        credit_score=680
    )
    
    print(f"\nStatus: {result['status']}")
    print(f"Products Found: {result['num_products_found']}")
    print(f"\nRecommended Products:")
    for product in result['products']:
        print(f"  - {product['section_title']} ({product['product_code']})")
        print(f"    Relevance: {product['relevance_score']}")

    assert result['status'] == 'success'

def test_first_time_homebuyer():
    """Test: First-time homebuyer query"""
    print("\n" + "="*80)
    print("TEST 3: First-Time Homebuyer")
    print("="*80)
    
    result = agent_bank_products(
        query="I'm a first-time homebuyer with $50,000 household income. What mortgage options do I have?",
        top_k=3,
        product_category="home_loans",
        income_range="$50,000"
    )
    
    print(f"\nStatus: {result['status']}")
    print(f"Enhanced Query: {result['enhanced_query']}")
    print(f"\nPerformance:")
    print(f"  Retrieval Time: {result['performance']['retrieval_time_ms']}ms")
    print(f"  Total Time: {result['performance']['total_time_ms']}ms")

    assert result['status'] == 'success'

def test_business_account():
    """Test: Small business account query"""
    print("\n" + "="*80)
    print("TEST 4: Small Business Account")
    print("="*80)
    
    result = agent_bank_products(
        query="I'm starting a small business and need a business checking account",
        top_k=2,
        product_category="business_accounts"
    )
    
    print(f"\nStatus: {result['status']}")
    print(f"\nAnswer:\n{result['answer']}")

    assert result['status'] == 'success'

def test_general_query():
    """Test: General query without category filter"""
    print("\n" + "="*80)
    print("TEST 5: General Query (No Category Filter)")
    print("="*80)
    
    result = agent_bank_products(
        query="I'm 22 years old, make $35,000, and want to start building my credit",
        top_k=5,
        product_category="all"
    )
    
    print(f"\nStatus: {result['status']}")
    print(f"Products Found: {result['num_products_found']}")
    print(f"\nProduct Categories:")
    categories = set([p['category'] for p in result['products']])
    for cat in categories:
        print(f"  - {cat}")

    assert result['status'] == 'success'

if __name__ == "__main__":
    print("🧪 Starting Bank Products Agent Tests...")
    
    try:
        test_savings_account_query()
        test_credit_card_query()
        test_first_time_homebuyer()
        test_business_account()
        test_general_query()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
```

**Run tests:**
```bash
python tests/test_bank_products_agent.py
```

---

### **Step 10: Verify MLflow Tracing**

After running tests, verify tracing in MLflow UI:

```bash
mlflow ui --port 5000
```

Navigate to: http://localhost:5000

**What to check:**
1. **Traces Tab:** Look for `bank_products_agent` traces
2. **Spans:** Verify you see:
   - `bank_products_request` (AGENT span)
   - `rag_retrieval` (RETRIEVER span)
   - `bank_products_response` (AGENT span)
3. **Inputs/Outputs:** Check that query, filters, and results are logged
4. **Performance Metrics:** Review retrieval time and total latency
5. **Similarity Scores:** Check that RAG retrieval scores are logged

**Expected trace structure:**
```
bank_products_agent (AGENT)
  ├─ bank_products_request (AGENT)
  ├─ rag_retrieval (RETRIEVER)
  │   ├─ Similarity scores: [0.85, 0.78, 0.72]
  │   └─ Retrieval time: 245ms
  └─ bank_products_response (AGENT)
      └─ Products: [SAV-002, SAV-001, SAV-003]
```

---

## 🎯 Completion Checklist

- [ ] **Step 1:** Added `tool_bank_products` to `tools_definitions.py`
- [ ] **Step 2:** Updated MLflow configuration with products agent tag
- [ ] **Step 3:** Added logging methods in `logging_service.py`
- [ ] **Step 4:** Created ChromaDB index with `create_products_index.py`
- [ ] **Step 5:** Implemented `agent_bank_products()` in `agents/agents.py`
- [ ] **Step 6:** Created bank products agent prompt
- [ ] **Step 7:** Updated `text2sql_engine.py` with products handler
- [ ] **Step 8:** Updated router prompt (see `BANK_PRODUCTS_ROUTER_PROMPT.md`)
- [ ] **Step 9:** Created and ran test script
- [ ] **Step 10:** Verified MLflow tracing works correctly

---

## 📊 Testing the Agent

### Via Test Script:
```bash
python tests/test_bank_products_agent.py
```

### Via API (if backend is running):
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I make $45,000 per year and want a savings account with high interest"
  }'
```

### Expected Behavior:
1. Router agent receives query
2. Router delegates to `tool_bank_products`
3. Bank products agent:
   - Loads ChromaDB index
   - Performs semantic search
   - Retrieves top 5 relevant products
   - Logs retrieval metrics
4. Response polished with product recommendations
5. Full trace visible in MLflow

---

## 🔧 Troubleshooting

### Issue: "Collection 'bank_products' not found"
**Solution:** Run `python scripts/create_products_index.py` first

### Issue: "No products retrieved"
**Solution:** 
- Check that `documents/bank_products_services.txt` exists
- Verify ChromaDB index was created successfully
- Check query is meaningful (not too vague)

### Issue: "MLflow traces not showing"
**Solution:**
- Verify `mlflow.openai.autolog()` is called at startup
- Check MLflow is tracking to correct experiment
- Ensure `@mlflow.trace` decorators are present

### Issue: "Low similarity scores (< 0.5)"
**Solution:**
- Enhance query with more context
- Check if product category filter is too restrictive
- Increase `top_k` to get more results

---

## 🚀 Next Steps

**Enhancements to consider:**
1. **Hybrid Search:** Combine semantic search with keyword filters (e.g., exact product codes)
2. **Personalization:** Store customer preferences and past interactions
3. **Eligibility Validation:** Automatically check if customer qualifies based on provided criteria
4. **Product Comparison:** Add tool to compare 2-3 products side-by-side
5. **Application Tracking:** Link to application system to help customers apply
6. **A/B Testing:** Use MLflow to test different prompts and retrieval strategies

**Additional Agents to Add:**
- **FAQ Agent:** General banking questions
- **Transaction Agent:** Help with account transactions and history
- **Investment Advisor Agent:** More sophisticated investment product recommendations
- **Fraud Detection Agent:** Security and fraud-related queries

---

## 📚 References

- **LlamaIndex Documentation:** https://docs.llamaindex.ai/
- **ChromaDB Documentation:** https://docs.trychroma.com/
- **MLflow Tracing Guide:** https://mlflow.org/docs/latest/llms/tracing/index.html
- **OpenAI Embeddings:** https://platform.openai.com/docs/guides/embeddings

---

**End of Guide** 🎉

You now have a fully functional Bank Products Agent with RAG, MLflow tracing, and comprehensive product recommendations!
