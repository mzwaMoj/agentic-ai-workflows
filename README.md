# Text2SQL API Application

A powerful FastAPI-based application that converts natural language queries into SQL and executes them with optional chart generation. This application provides a seamless interface for business users to interact with databases using plain English.

## 🏗️ Architecture Overview

This application follows a modular, service-oriented architecture designed for scalability, maintainability, and easy integration with frontend applications (React, Angular, etc.).

```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend                               │
│                    (React, Web UI, etc.)                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────────────────────┐
│                      FastAPI Application                       │
│                        (main.py)                               │
├─────────────────────────────────────────────────────────────────┤
│                     API Layer (v1)                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │   Health    │ │  Text2SQL   │ │    Chat     │              │
│  │ Endpoints   │ │ Endpoints   │ │ Endpoints   │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                   Core Business Logic                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Text2SQL Engine                               ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          ││
│  │  │   Router    │ │     SQL     │ │    Chart    │          ││
│  │  │   Agent     │ │   Agent     │ │   Agent     │          ││
│  │  └─────────────┘ └─────────────┘ └─────────────┘          ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                     Service Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │   OpenAI    │ │  Database   │ │   Vector    │              │
│  │  Service    │ │  Service    │ │  Service    │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                   External Services                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │   Azure     │ │  SQL Server │ │  ChromaDB   │              │
│  │  OpenAI     │ │  Database   │ │ (Metadata)  │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 How It Works - Step by Step Process

### Step 1: User Query Input
- User submits a natural language query via REST API
- Examples: "Show me all customers", "What are the top 5 products by sales?"
- Query is validated and sanitized

### Step 2: Query Routing & Analysis
```
User Query → Router Agent → Intent Analysis
                ↓
    ┌─────────────────────────────┐
    │  Query Classification:      │
    │  • SQL Required?            │
    │  • Table Requirements?      │
    │  • Chart Generation?        │
    │  • General Conversation?    │
    └─────────────────────────────┘
```

### Step 3: Table Metadata Retrieval
- Vector database (ChromaDB) contains pre-indexed table metadata
- Semantic search finds relevant tables and columns
- Provides context about available data structures

### Step 4: SQL Generation
```
Natural Language + Table Metadata → Azure OpenAI → SQL Query
    ↓
"Show customers in New York" + Customer_Table_Schema → 
"SELECT * FROM customers WHERE city = 'New York'"
```

### Step 5: SQL Validation & Execution
- Safety checks prevent destructive operations (DELETE, DROP, etc.)
- Query execution with result limits
- Error handling for invalid queries

### Step 6: Chart Generation (Optional)
- Analyzes SQL results for chart potential
- Generates interactive charts using Plotly
- Returns HTML/JavaScript for frontend embedding

### Step 7: Response Generation
- Combines SQL results, charts, and natural language explanation
- Formatted response with execution metadata
- Chat history maintenance for conversational flow

## 📋 API Endpoints

### Health Endpoints
```
GET /api/v1/health              # Basic health check
GET /api/v1/health/detailed     # Detailed service status
```

### Text2SQL Endpoints
```
POST /api/v1/text2sql/generate  # Generate SQL from natural language
POST /api/v1/text2sql/execute   # Execute SQL directly
POST /api/v1/text2sql/validate  # Validate SQL query
GET  /api/v1/text2sql/tables    # Get table information
```

### Chat Endpoints
```
POST /api/v1/chat/completions   # Conversational interface
POST /api/v1/chat/history       # Chat session management
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Azure OpenAI access
- SQL Server access
- Virtual environment (recommended)

### Step 1: Clone and Setup Environment
```powershell
# Clone the repository
git clone <repository-url>
cd text_sql_analysis

# Create and activate virtual environment
python -m venv venv
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration
Create a `.env` file in the root directory:

```env
# Application Configuration
APP_NAME=Text2SQL API
APP_VERSION=1.0.0
DEBUG=true

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your_azure_openai_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_VERSION=2024-02-15-preview

# Database Configuration
DB_SERVER=your_sql_server_here
DB_DATABASE=master
DB_AUTH_TYPE=windows

# Vector Database Configuration
VECTOR_DB_PATH=./index/chroma_db

# API Configuration
CORS_ORIGINS=*
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

# Feature Flags
ENABLE_CHAT=true
ENABLE_CHARTS=true
ENABLE_MLFLOW=true
```

### Step 3: Database Setup
```powershell
# Run database setup scripts
python db/db_setup.py

# Generate sample data (optional)
python db/generate_sql_data.py
```

### Step 4: Start the Application
```powershell
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The application will be available at:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Root Endpoint**: http://localhost:8000/

## 🔍 Detailed Process Flow

### 1. Request Processing Pipeline
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  HTTP Request   │───▶│   Validation    │───▶│   Middleware    │
│   (FastAPI)     │    │   (Pydantic)    │    │   (CORS, etc.)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
           │                                              │
           ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Text2SQL       │◀───│   Dependency    │◀───│   Router        │
│  Engine         │    │   Injection     │    │  (Endpoint)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. Core Engine Processing
```
┌─────────────────┐
│   User Query    │
│ "Show top 5     │
│  customers"     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│  Router Agent   │───▶│  Intent: SQL    │
│  Classification │    │  Tables: Yes    │
└────────┬────────┘    │  Charts: Maybe  │
         │             └─────────────────┘
         ▼
┌─────────────────┐    ┌─────────────────┐
│ Table Retriever │───▶│ Vector Search   │
│ (ChromaDB)      │    │ → Customer      │
└────────┬────────┘    │   Tables Found  │
         │             └─────────────────┘
         ▼
┌─────────────────┐    ┌─────────────────┐
│   SQL Agent     │───▶│ Generated SQL:  │
│ (Azure OpenAI)  │    │ SELECT TOP 5... │
└────────┬────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│ Database        │───▶│   SQL Results   │
│ Execution       │    │   (Validated)   │
└────────┬────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│  Chart Agent    │───▶│  Chart HTML     │
│ (If applicable) │    │ (Plotly/D3)     │
└────────┬────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│  Final Agent    │───▶│ Natural Language│
│ (Response Gen)  │    │   Response      │
└─────────────────┘    └─────────────────┘
```

### 3. Service Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                     Service Container                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  OpenAI Service │  │Database Service │  │ Vector Service  │ │
│  │                 │  │                 │  │                 │ │
│  │ • Chat          │  │ • Connection    │  │ • Embedding     │ │
│  │ • Completion    │  │ • Query Exec    │  │ • Search        │ │
│  │ • Validation    │  │ • Result Parse  │  │ • Metadata      │ │
│  │ • Health Check  │  │ • Health Check  │  │ • Health Check  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Logging Service │  │   Config        │  │ Error Handler   │ │
│  │                 │  │   Service       │  │                 │ │
│  │ • MLflow Track  │  │ • Settings      │  │ • Exception     │ │
│  │ • Performance   │  │ • Validation    │  │ • Response      │ │
│  │ • Error Logs    │  │ • Environment   │  │ • HTTP Codes    │ │
│  │ • Metrics       │  │ • Features      │  │ • Debug Info    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow Diagram

### Query Processing Flow
```
[User Input] → [Request Validation] → [Router Agent] → [Intent Analysis]
                                                            │
                                                            ▼
[Response Generation] ← [Chart Agent] ← [SQL Execution] ← [SQL Agent]
         │                                                   │
         ▼                                                   ▼
[Final Response] ← [Natural Language] ← [Table Retriever] ← [Vector Search]
```

### Database Integration Flow
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SQL Server    │    │   ChromaDB      │    │   Azure OpenAI  │
│                 │    │                 │    │                 │
│ • Customer Data │◀───│ • Table Meta    │◀───│ • SQL Generation│
│ • Transaction   │    │ • Column Info   │    │ • NL Processing │
│ • Product Info  │    │ • Relationships │    │ • Chart Logic   │
│ • Sales Data    │    │ • Descriptions  │    │ • Response Gen  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │  Database       │    │   Vector        │    │   OpenAI        │
    │  Service        │    │   Service       │    │   Service       │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🧪 Testing the Application

### 1. Health Check Test
```powershell
# Basic health check
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method GET

# Detailed health check
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/detailed" -Method GET
```

### 2. Text2SQL Test
```powershell
# Simple query test
$body = @{
    query = "Show me all customers"
    include_charts = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/text2sql/generate" -Method POST -Body $body -ContentType "application/json"
```

### 3. Chart Generation Test
```powershell
# Query with chart generation
$body = @{
    query = "Show sales by month for the last year"
    include_charts = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/text2sql/generate" -Method POST -Body $body -ContentType "application/json"
```

### 4. Chat Interface Test
```powershell
# Conversational interaction
$body = @{
    message = "What are our top performing products?"
    include_charts = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/chat/completions" -Method POST -Body $body -ContentType "application/json"
```

## 📝 Example Usage Scenarios

### Scenario 1: Business Analytics Query
**Input**: "What are the top 5 customers by total purchase amount?"

**Process**:
1. Router identifies this as a SQL query requiring aggregation
2. Table Retriever finds customer and sales tables
3. SQL Agent generates: `SELECT TOP 5 c.customer_name, SUM(s.amount) as total FROM customers c JOIN sales s ON c.id = s.customer_id GROUP BY c.customer_name ORDER BY total DESC`
4. Database executes query with safety checks
5. Chart Agent creates a bar chart visualization
6. Final response combines results with explanation

**Output**:
```json
{
  "success": true,
  "response": "Here are the top 5 customers by total purchase amount...",
  "sql_query": "SELECT TOP 5...",
  "sql_results": [...],
  "chart_html": "<div>...</div>",
  "execution_time": 0.234
}
```

### Scenario 2: Conversational Follow-up
**Input**: "Show me their contact information too"

**Process**:
1. Router uses chat history context
2. Understands "their" refers to previous top 5 customers
3. Modifies previous query to include contact fields
4. Generates response maintaining conversation flow

## 🔧 Configuration Options

### Feature Flags
- `ENABLE_CHAT`: Enable conversational interface
- `ENABLE_CHARTS`: Enable chart generation
- `ENABLE_MLFLOW`: Enable performance tracking
- `DEBUG`: Enable debug mode with detailed errors

### Security Settings
- `API_KEY`: Optional API key authentication
- `CORS_ORIGINS`: Configure allowed origins
- `MAX_QUERY_LENGTH`: Limit query size
- `RATE_LIMITING`: Configure request limits

### Performance Tuning
- `DB_CONNECTION_POOL`: Database connection pooling
- `OPENAI_TIMEOUT`: AI service timeouts
- `CACHE_TTL`: Result caching duration
- `MAX_RESULTS`: Limit result set sizes

## 🚀 Deployment Options

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Azure Container Apps
- Serverless container deployment
- Auto-scaling based on demand
- Integration with Azure services

### Traditional Server
- Install Python 3.11+
- Configure reverse proxy (nginx)
- Set up SSL certificates
- Configure monitoring

## 🔍 Troubleshooting

### Common Issues

1. **Azure OpenAI Connection Error**
   - Verify endpoint URL and API key
   - Check network connectivity
   - Validate deployment name

2. **Database Connection Failed**
   - Confirm SQL Server accessibility
   - Check authentication credentials
   - Verify firewall settings

3. **Vector Database Issues**
   - Ensure ChromaDB path exists
   - Check file permissions
   - Verify metadata initialization

4. **Query Generation Problems**
   - Review table metadata quality
   - Check prompt configuration
   - Validate model deployment

### Debug Mode
Enable debug mode by setting `DEBUG=true` in environment variables for detailed error information and request logging.

### Logging
Application logs are available in:
- Console output (development)
- MLflow tracking (production)
- Custom log files (configurable)

## 📚 API Documentation

When running in debug mode, comprehensive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

The documentation includes:
- Interactive API testing
- Request/response schemas
- Authentication requirements
- Error code explanations

## 🔒 Security Considerations

### Input Validation
- All user inputs are validated and sanitized
- SQL injection prevention through parameterized queries
- Maximum query length limits

### SQL Safety
- Blacklist of dangerous SQL operations (DROP, DELETE, etc.)
- Query analysis before execution
- Result size limitations

### Authentication
- Optional API key authentication
- CORS configuration for frontend integration
- Rate limiting capabilities

### Error Handling
- Secure error messages in production
- Detailed debugging information in development
- Logging of security events

## 🤝 Frontend Integration

### React Example
```javascript
const TextToSQLClient = {
  generateSQL: async (query) => {
    const response = await fetch('/api/v1/text2sql/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        query, 
        include_charts: true 
      })
    });
    return response.json();
  },

  chat: async (message, history = []) => {
    const response = await fetch('/api/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message, 
        chat_history: history,
        include_charts: true 
      })
    });
    return response.json();
  }
};
```

### Chart Integration
The application generates chart HTML that can be directly embedded in frontend applications. Charts are built with Plotly.js for interactive data visualization.

## 📈 Performance Monitoring

### MLflow Integration
- Request/response tracking
- Performance metrics
- Error rate monitoring
- Model performance analysis

### Health Checks
- Service availability monitoring
- Database connectivity checks
- Azure OpenAI service status
- Vector database health

### Metrics
- Query execution times
- API response times
- Error rates and types
- Resource utilization

## 🛣️ Roadmap

### Planned Features
- [ ] Advanced chart types (D3.js integration)
- [ ] Multi-database support
- [ ] Advanced caching layer
- [ ] Real-time query streaming
- [ ] Advanced security features
- [ ] Performance optimizations
- [ ] Enhanced error recovery

### Future Enhancements
- [ ] Natural language explanations for charts
- [ ] Query suggestion engine
- [ ] Advanced analytics capabilities
- [ ] Custom visualization builder
- [ ] Multi-tenant support

---

## 📞 Support

For support and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Enable debug mode for detailed logging
4. Check application logs and health endpoints

This application represents a production-ready, enterprise-grade solution for natural language to SQL conversion with advanced features for business intelligence and data analysis.
