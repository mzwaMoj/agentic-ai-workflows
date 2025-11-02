# Scaling Agentic AI: Building Reliable, Traceable, and High-Impact Systems

**Duration:** 30 minutes  
**Focus:** Developer introduction to observability, tracing, and agent orchestration

---

## Slide 1: Title Slide

**Scaling Agentic AI**  
*Building Reliable, Traceable, and High-Impact Systems*

**Demo Tech Stack:**
- OpenAI LLMs (Agent Intelligence)
- MLflow (Experimentation & Tracing)
- LlamaIndex + ChromaDB (RAG Pipeline)
- Azure Data Studio (Text2SQL)
- Function Calling & Tools

---

## Slide 2: Why This Matters

**The Challenge: From Prototype to Production**

❌ **Common Problems:**
- "It worked in my Jupyter notebook, but fails in production"
- "Which prompt version caused this regression?"
- "Why did the agent make this decision?"
- "How do I add new capabilities without breaking existing ones?"

✅ **What We Need:**
- **Traceability** - See every agent decision
- **Versioning** - Track prompt evolution
- **Observability** - Understand system behavior
- **Scalability** - Grow features AND performance

---

## Slide 3: Two Dimensions of Scaling

### 🎯 Feature Scaling (Functional)
**Problem:** Single agent, complex prompt, managing everything  
**Solution:** Multi-Agent Systems (MAS)

```
Monolithic Agent          →    Specialized Agents
├── Generate SQL                ├── SQL Generator Agent
├── Validate Query              ├── Query Validator Agent
├── Execute & Format            ├── Execution Agent
└── Create Visualization        └── Visualization Agent
```

### 🚀 Performance Scaling (Throughput)
**Problem:** Slow response, can't handle concurrent users  
**Solution:** Infrastructure migration

```
Local/Prototype            →    Production
├── ChromaDB (in-memory)        ├── Qdrant/Weaviate (distributed)
├── SQLite/DuckDB               ├── PostgreSQL/Azure SQL
└── Single process              └── Cloud compute (containers)
```

---

## Slide 4: The Observability Problem

**Without Tracing:**
```
User Question → [BLACK BOX] → Answer
                    ❓
```

**With MLflow Tracing:**
```
User Question
  ├─ Agent 1: Query Planning (120ms)
  │   ├─ LLM Call: gpt-4o (80ms)
  │   └─ Table Retrieval (40ms)
  ├─ Agent 2: SQL Generation (200ms)
  │   ├─ Schema Lookup (30ms)
  │   ├─ LLM Call: gpt-4o (150ms)
  │   └─ Validation (20ms)
  └─ Agent 3: Execution (500ms)
      ├─ Database Query (480ms)
      └─ Result Formatting (20ms)
```

**We can now:**
- See bottlenecks (database query = 480ms)
- Debug failures at exact span
- Track costs per agent

---

## Slide 5: Demo Architecture Overview

```
┌─────────────────────────────────────────────────┐
│            User Query (Natural Language)         │
└────────────────────┬────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │   Agent Orchestrator │ ◄─── MLflow Tracing
          │   (Function Calling) │
          └──────────┬──────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼───┐   ┌───▼───┐   ┌───▼────┐
    │ SQL   │   │ RAG   │   │Viz     │
    │ Agent │   │ Agent │   │Agent   │
    └───┬───┘   └───┬───┘   └───┬────┘
        │           │            │
    ┌───▼────┐  ┌──▼─────┐  ┌───▼────┐
    │ Azure  │  │ChromaDB│  │Chart   │
    │  SQL   │  │LlamaIdx│  │Lib     │
    └────────┘  └────────┘  └────────┘
```

---

## Slide 6: Core Component #1 - Agent Framework

**OpenAI Function Calling**

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "text_to_sql",
            "description": "Convert natural language to SQL query",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "database": {"type": "string"}
                }
            }
        }
    }
]

# Agent decides WHEN to call which tool
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto"  # Let agent decide
)
```

**Key Benefit:** Agent autonomy + structured outputs

---

## Slide 7: Core Component #2 - MLflow Tracing

**Why MLflow for Agent Systems?**

1. **Automatic Span Tracking**
   - Captures every LLM call
   - Records tool/function invocations
   - Measures latency per operation

2. **Prompt Versioning**
   - Track prompt changes over time
   - A/B test different prompt strategies
   - Rollback to previous versions

3. **Experiment Comparison**
   ```python
   import mlflow
   
   # Version 1: Basic prompt
   with mlflow.start_run(run_name="basic_prompt_v1"):
       mlflow.log_param("prompt_version", "v1.0")
       mlflow.log_param("model", "gpt-4o")
       result = agent.run(query)
       mlflow.log_metric("accuracy", 0.85)
   
   # Version 2: Enhanced with examples
   with mlflow.start_run(run_name="enhanced_prompt_v2"):
       mlflow.log_param("prompt_version", "v2.0")
       result = agent.run(query)
       mlflow.log_metric("accuracy", 0.92)
   ```

---

## Slide 8: Core Component #3 - RAG Pipeline

**LlamaIndex + ChromaDB**

```python
from llama_index import VectorStoreIndex, Document
from chromadb import Client

# 1. Create embeddings from table metadata
documents = [
    Document(text="Table: sales, Columns: id, date, amount, customer_id"),
    Document(text="Table: customers, Columns: id, name, email, region")
]

# 2. Store in vector database
index = VectorStoreIndex.from_documents(documents)

# 3. Retrieve relevant context
query = "Show me sales by region"
retriever = index.as_retriever(similarity_top_k=3)
relevant_tables = retriever.retrieve(query)

# 4. Pass to SQL agent
sql_agent.generate_query(query, context=relevant_tables)
```

**Why This Matters:**
- Handles large schemas (100+ tables)
- Finds relevant tables automatically
- Reduces prompt size & improves accuracy

---

## Slide 9: Guardrails - Keeping Agents Safe

**The Problem:**
- Agents can generate harmful SQL (DROP TABLE)
- May expose sensitive data
- Could produce incorrect results

**Solution: Multi-Layer Guardrails**

```python
# 1. Pre-execution validation
def validate_sql(query: str) -> bool:
    blocked_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
    if any(keyword in query.upper() for keyword in blocked_keywords):
        raise SecurityError("Destructive operation blocked")
    return True

# 2. Schema validation
def check_table_access(query: str, allowed_tables: list) -> bool:
    parsed_tables = extract_tables(query)
    if not all(t in allowed_tables for t in parsed_tables):
        raise PermissionError("Unauthorized table access")
    return True

# 3. Result validation
def validate_result(df: DataFrame) -> bool:
    if df.empty:
        logger.warning("Query returned no results")
    if len(df) > 10000:
        raise ValueError("Result set too large")
    return True
```

---

## Slide 10: Demo Flow - Part 1

**Live Demo: Text2SQL with Tracing**

1. **User asks:** "What were total sales last quarter?"

2. **MLflow captures:**
   ```
   Trace: text2sql_query_20251101_143022
   ├─ Span: table_retrieval (embeddings)
   │   ├─ Input: "total sales last quarter"
   │   ├─ ChromaDB query: 45ms
   │   └─ Output: [sales, time_dimension]
   ├─ Span: sql_generation
   │   ├─ Prompt Version: v2.3
   │   ├─ Model: gpt-4o
   │   ├─ Generated SQL: SELECT SUM(amount)...
   │   └─ Latency: 180ms
   └─ Span: query_execution
       ├─ Database: Azure SQL
       ├─ Execution time: 520ms
       └─ Rows returned: 1
   ```

3. **We explore:** MLflow UI showing spans, decisions, timing

---

## Slide 11: Demo Flow - Part 2

**Live Demo: Adding a New Agent**

**Scenario:** Add a "Data Quality Agent" to check results

```python
# 1. Define new tool
data_quality_tool = {
    "type": "function",
    "function": {
        "name": "check_data_quality",
        "description": "Validate query results for anomalies",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {"type": "array"},
                "checks": {"type": "array"}
            }
        }
    }
}

# 2. Implement agent function
@mlflow.trace
def check_data_quality(data, checks):
    results = {}
    if "null_check" in checks:
        results["nulls"] = data.isnull().sum()
    if "outlier_check" in checks:
        results["outliers"] = detect_outliers(data)
    return results

# 3. Register with orchestrator
agent_registry.register("data_quality", check_data_quality, data_quality_tool)
```

**Key Point:** Function calling makes agents pluggable!

---

## Slide 12: Open Source Tools Ecosystem

### 🛠️ **Agent Development**
- **OpenAI SDK** - Function calling, structured outputs
- **LangChain** - Agent chains, memory management
- **CrewAI** - Multi-agent orchestration
- **LlamaIndex** - RAG framework

### 📊 **Observability & Tracing**
- **MLflow** - Experiment tracking, tracing, model registry
- **LangSmith** - LangChain-specific tracing
- **Phoenix** - Open-source LLM observability
- **OpenTelemetry** - Distributed tracing standard

### 🎯 **Evaluation**
- **DeepEval** - LLM evaluation framework
- **RAGAS** - RAG-specific metrics
- **PromptFoo** - Prompt testing & comparison

### 💾 **Vector Databases**
- **ChromaDB** - Lightweight, local development
- **Qdrant** - Production-scale, distributed
- **Weaviate** - GraphQL API, ML-first

---

## Slide 13: Evaluation Metrics for Agents

**Why Evaluate?**
- Agents are non-deterministic
- Need quantitative measures of quality
- Track improvements over time

### 📏 **Key Metrics**

| Metric | What It Measures | Tool |
|--------|------------------|------|
| **Accuracy** | Correct answers / Total queries | Custom |
| **SQL Validity** | % of generated queries that execute | DeepEval |
| **Semantic Similarity** | Result matches expected answer | RAGAS |
| **Latency** | End-to-end response time | MLflow |
| **Context Precision** | Relevant retrieved docs / Total docs | RAGAS |
| **Hallucination Rate** | Answers not grounded in data | DeepEval |
| **Tool Call Success** | Successful function calls / Attempted | MLflow |

```python
# Example: Automated evaluation
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
    input="Total sales last quarter?",
    actual_output=agent_response,
    expected_output="$1.2M in Q4 2024"
)

metric = AnswerRelevancyMetric(threshold=0.8)
score = metric.measure(test_case)
mlflow.log_metric("answer_relevancy", score)
```

---

## Slide 14: Scaling Strategy Matrix

| Dimension | Prototype (Local) | Production (Scale) |
|-----------|-------------------|-------------------|
| **Feature Complexity** | Single agent<br/>Monolithic prompt | Multi-agent system<br/>Specialized agents |
| **Orchestration** | Sequential calls | LangGraph/CrewAI<br/>Parallel execution |
| **Data Storage** | ChromaDB (in-memory)<br/>SQLite/DuckDB | Qdrant/Weaviate<br/>Azure SQL/PostgreSQL |
| **Tracing** | MLflow (local) | MLflow + Cloud logging<br/>Datadog/Arize |
| **Evaluation** | Manual testing | Automated CI/CD tests<br/>A/B testing |
| **Deployment** | Local script | Docker containers<br/>Azure Functions/Fargate |
| **Guardrails** | Basic validation | Enterprise policies<br/>Guardian agents |

**Key Insight:** Start simple, scale intentionally based on bottlenecks

---

## Slide 15: Best Practices - What We Learned

### ✅ **DO:**
1. **Start with tracing from day one** - MLflow setup takes 5 minutes, saves hours of debugging
2. **Version everything** - Prompts, models, data schemas
3. **Instrument each agent** - Use `@mlflow.trace` decorator liberally
4. **Build modular agents** - Function calling enables plug-and-play
5. **Evaluate continuously** - Automate metric collection

### ❌ **DON'T:**
1. **Over-engineer early** - ChromaDB is fine for prototypes
2. **Skip guardrails** - Always validate before execution
3. **Ignore costs** - Track token usage per agent
4. **Use single mega-prompt** - Split into specialized agents
5. **Deploy without observability** - You'll regret it

---

## Slide 16: Live Demo Checklist

**What We'll Show:**

✅ **Part 1: Basic Flow (10 min)**
- Natural language query → SQL generation
- MLflow trace inspection
- Viewing spans and agent decisions
- Azure Data Studio query execution

✅ **Part 2: RAG Pipeline (5 min)**
- Table metadata embeddings in ChromaDB
- Semantic search for relevant tables
- Context injection into SQL agent

✅ **Part 3: Adding New Agent (10 min)**
- Define new function/tool
- Register with orchestrator
- Test with tracing
- Compare prompt versions

✅ **Part 4: Guardrails (5 min)**
- Show blocked destructive query
- Schema validation
- Result size limits

---

## Slide 17: Key Takeaways

### 🎯 **Three Core Principles**

1. **Traceability is Non-Negotiable**
   - Every decision should be observable
   - Use MLflow traces to understand agent behavior
   - Debug 10x faster with proper instrumentation

2. **Scale Intentionally**
   - Feature complexity ≠ Performance throughput
   - Multi-agent systems for complex tasks
   - Distributed infrastructure for concurrent users

3. **Evaluate Relentlessly**
   - Agents are probabilistic - measure everything
   - Automate evaluation in CI/CD
   - Track metrics over time (accuracy, latency, cost)

---

## Slide 18: Resources & Next Steps

### 📚 **Learn More**
- **MLflow Tracing Docs:** https://mlflow.org/docs/latest/llms/tracing
- **OpenAI Function Calling:** https://platform.openai.com/docs/guides/function-calling
- **LlamaIndex:** https://docs.llamaindex.ai
- **RAGAS Metrics:** https://docs.ragas.io

### 🚀 **Try It Yourself**
```bash
# Clone demo repository
git clone [your-repo]

# Install dependencies
pip install -r requirements.txt

# Start MLflow UI
mlflow ui

# Run demo
python app/main.py
```

### 💡 **Questions?**
- GitHub: [your-github]
- Email: [your-email]
- Demo Code: [repo-link]

---

## Slide 19: Q&A

**Common Questions:**

**Q: How much does MLflow tracing impact performance?**  
A: ~5-10ms overhead per span. Negligible compared to LLM calls (100-500ms).

**Q: Can I use this with other LLM providers (Anthropic, Cohere)?**  
A: Yes! MLflow and LlamaIndex support multiple providers.

**Q: When should I move from ChromaDB to Qdrant?**  
A: When you need: (1) >100M vectors, (2) multi-node deployment, or (3) advanced filtering.

**Q: How do I handle agent failures gracefully?**  
A: Use try/except with fallback agents, implement retry logic, and log failures to MLflow.

---

## Slide 20: Thank You!

**Scaling Agentic AI: Building Reliable, Traceable, and High-Impact Systems**

**Remember:**
- 🔍 Trace everything (MLflow)
- 🧩 Build modular agents (Function calling)
- 📊 Measure relentlessly (Evaluation metrics)
- 🛡️ Guard your systems (Validation layers)
- 🚀 Scale intentionally (Feature vs. Performance)

**Let's build better AI systems together!**

---

## Appendix: Technical Details

### MLflow Setup
```python
import mlflow

# Enable autologging for OpenAI
mlflow.openai.autolog()

# Manual tracing
@mlflow.trace(name="sql_generation", span_type="AGENT")
def generate_sql(question: str, context: dict):
    # Your agent logic
    return sql_query

# View traces
mlflow.set_tracking_uri("http://localhost:5000")
```

### Function Calling Schema
```python
# Strict mode for deterministic outputs
tool_schema = {
    "type": "function",
    "function": {
        "name": "execute_sql",
        "strict": True,  # Enforces schema compliance
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "database": {"type": "string", "enum": ["sales", "analytics"]}
            },
            "required": ["query", "database"],
            "additionalProperties": False
        }
    }
}
```

### Evaluation Pipeline
```python
from deepeval import assert_test
from deepeval.metrics import GEval

def test_sql_agent():
    test_cases = load_test_cases()
    
    for case in test_cases:
        with mlflow.start_run():
            response = agent.run(case.input)
            
            # Log to MLflow
            mlflow.log_param("test_case", case.id)
            mlflow.log_metric("execution_time", response.latency)
            
            # Evaluate
            correctness = GEval(name="SQL Correctness")
            score = correctness.measure(case, response)
            mlflow.log_metric("correctness_score", score)
            
            assert_test(score > 0.8)
```

---

**End of Presentation**
