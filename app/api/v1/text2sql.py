"""
Text2SQL endpoints for natural language to SQL conversion.
"""

import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from typing import Dict, Any

from app.models import (
    Text2SQLRequest, 
    Text2SQLResponse,
    SQLExecuteRequest,
    SQLExecuteResponse,
    QueryValidationRequest,
    QueryValidationResponse,
    TableInfoRequest,
    TableInfoResponse,
    ErrorResponse
)
from app.core import Text2SQLEngine
from app.services import get_services

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_text2sql_engine(services: Dict[str, Any] = Depends(get_services)) -> Text2SQLEngine:
    """Dependency to get Text2SQL engine instance."""
    return Text2SQLEngine(services)


@router.post("/generate", response_model=Text2SQLResponse)
async def generate_sql(
    request: Text2SQLRequest,
    engine: Text2SQLEngine = Depends(get_text2sql_engine)
):
    """
    🎯 **Generate SQL from Natural Language**
    
    Convert a natural language question into SQL, execute it, and get results with optional charts.
    
    ### 📝 **What this endpoint does:**
    1. **Analyzes** your natural language question
    2. **Converts** it to appropriate SQL query
    3. **Executes** the query against the database
    4. **Generates** charts/visualizations if requested
    5. **Returns** formatted results with natural language explanation
    
    ### 💡 **Example Questions:**
    - "Which client has the highest account balance?"
    - "What are the quarterly transaction volumes?"
    - "How many closed accounts are there?"
    - "Show me customer demographics by age group"
    - "What's the average transaction amount by month?"
    
    ### 📊 **Chart Generation:**
    Set `include_charts: true` to automatically generate visualizations when appropriate.
    Charts are returned as HTML that can be embedded directly in web pages.
    
    ### 🔄 **Chat History:**
    Include previous conversation context for follow-up questions:
    - "Show me more details about that"
    - "Can you make a chart of this data?"
    - "What about the previous quarter?"
    
    ### ⚡ **Performance:**
    - Typical response time: 1-3 seconds
    - Uses vector search for intelligent table selection
    - Optimized SQL generation with Azure OpenAI
    """
    start_time = time.time()
    
    try:
        # Validate the query first
        validation = await engine.validate_query(request.query)
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid query: {'; '.join(validation['warnings'])}"
            )
        
        # Process the query
        result = await engine.process_query(
            user_input=request.query,
            chat_history=request.chat_history
        )
        execution_time = time.time() - start_time
        
        if result["success"]:
            return Text2SQLResponse(
                success=True,
                response=result["response"],
                sql_query=result.get("sql_code"),  # Use the actual generated SQL code
                sql_results=result.get("sql_results"),
                chart_html=result.get("chart_html"),
                execution_time=execution_time,
                chat_history=result.get("chat_history"),
                routing_info=result.get("routing_info")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Query processing failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text2SQL generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/execute", response_model=SQLExecuteResponse)
async def execute_sql(
    request: SQLExecuteRequest,
    engine: Text2SQLEngine = Depends(get_text2sql_engine)
):
    """
    Execute a SQL query directly.
    
    This endpoint allows direct execution of SQL queries with validation.
    """
    start_time = time.time()
    
    try:
        # Get database service
        db_service = engine.database_service
        
        # Validate SQL if requested or if validation_only is True
        is_valid = await db_service.validate_sql(request.sql_query)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid SQL query syntax"
            )
        
        if request.validate_only:
            return SQLExecuteResponse(
                success=True,
                results=None,
                sql_query=request.sql_query,
                execution_time=time.time() - start_time,
                validation_only=True
            )
        
        # Execute the SQL query
        results = await db_service.execute_sql(request.sql_query)
        
        # Process results
        processed_results = []
        row_count = 0
        
        for result in results:
            if isinstance(result, dict) and result.get("status") == "success":
                data = result.get("data", [])
                if isinstance(data, list):
                    row_count += len(data)
                processed_results.append(result)
            else:
                # Handle errors
                error_msg = result.get("error", "Query execution failed")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
        
        execution_time = time.time() - start_time
        
        return SQLExecuteResponse(
            success=True,
            results=processed_results,
            row_count=row_count,
            execution_time=execution_time,
            sql_query=request.sql_query,
            validation_only=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SQL execution error: {str(e)}"
        )


@router.post("/validate", response_model=QueryValidationResponse)
async def validate_query(
    request: QueryValidationRequest,
    engine: Text2SQLEngine = Depends(get_text2sql_engine)
):
    """
    Validate a query without executing it.
    
    This endpoint validates both natural language and SQL queries.
    """
    try:
        if request.query_type == "sql":
            # Validate SQL syntax
            db_service = engine.database_service
            is_valid = await db_service.validate_sql(request.query)
            
            return QueryValidationResponse(
                is_valid=is_valid,
                query_type="sql",
                warnings=[] if is_valid else ["SQL syntax validation failed"],
                suggestions=["Check SQL syntax and table names"] if not is_valid else []
            )
        else:
            # Validate natural language query
            validation = await engine.validate_query(request.query)
            
            return QueryValidationResponse(
                is_valid=validation["is_valid"],
                warnings=validation.get("warnings", []),
                suggestions=validation.get("suggestions", []),
                query_type="natural_language"
            )
            
    except Exception as e:
        logger.error(f"Query validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation error: {str(e)}"
        )


@router.get("/tables", response_model=TableInfoResponse)
async def get_table_info(
    request: TableInfoRequest = Depends(),
    engine: Text2SQLEngine = Depends(get_text2sql_engine)
):
    """
    Get information about available database tables.
    
    This endpoint returns metadata about tables available for querying.
    """
    try:
        table_retriever = engine.table_retriever
        
        if request.table_name:
            # Get specific table schema
            schema = await table_retriever.get_table_schema(request.table_name)
            if schema:
                tables = [{
                    "table_name": request.table_name,
                    "schema": schema if request.include_schema else None
                }]
                return TableInfoResponse(
                    success=True,
                    tables=tables,
                    total_tables=1
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Table '{request.table_name}' not found"
                )
        else:
            # Get all available tables
            available_tables = await table_retriever.list_available_tables()
            
            tables = []
            for table_name in available_tables:
                table_info = {"table_name": table_name}
                if request.include_schema:
                    schema = await table_retriever.get_table_schema(table_name)
                    table_info["schema"] = schema
                tables.append(table_info)
            
            # Get collection status
            vector_service = engine.vector_service
            collection_info = await vector_service.get_collection_info()
            
            return TableInfoResponse(
                success=True,
                tables=tables,
                total_tables=len(tables),
                collection_status=collection_info.get("status", "unknown")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Table info retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve table information: {str(e)}"
        )


@router.get("/explain/{query_id}")
async def explain_query(
    query_id: str,
    engine: Text2SQLEngine = Depends(get_text2sql_engine)
):
    """
    Explain a previously executed query.
    
    This endpoint provides natural language explanations of SQL queries.
    """
    try:
        # In a real implementation, you'd look up the query by ID
        # For now, return a placeholder response
        return {
            "query_id": query_id,
            "explanation": "Query explanation feature is not yet implemented",
            "suggestion": "Use the /validate endpoint for query analysis"
        }
        
    except Exception as e:
        logger.error(f"Query explanation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explanation error: {str(e)}"
        )


@router.post("/generate-chart", response_class=HTMLResponse)
async def generate_chart_view(
    request: Text2SQLRequest,
    engine: Text2SQLEngine = Depends(get_text2sql_engine)
):
    """
    🎨 **Generate and View Chart Directly**
    
    This endpoint generates a chart from your query and returns it as viewable HTML.
    Perfect for testing and viewing charts directly in your browser!
    
    ### 🎯 **What this endpoint does:**
    1. **Processes** your natural language query
    2. **Generates** SQL and executes it
    3. **Creates** interactive chart visualization
    4. **Returns** the chart as viewable HTML page
    
    ### 💡 **Example Chart Queries:**
    - "Show me a pie chart of transaction types"
    - "Create a bar chart of customer balances by income category"
    - "Plot a line chart of monthly transaction volumes"
    - "Generate a scatter plot of income vs credit score"
    
    ### 🌟 **Features:**
    - **Interactive charts** with zoom, hover, and filtering
    - **Professional styling** with Plotly themes
    - **Responsive design** that works on all devices
    - **Direct viewing** - no need to parse HTML strings
    """
    try:
        # Process the query to get chart
        result = await engine.process_query(
            user_input=request.query,
            chat_history=request.chat_history or []
        )
        
        if result["success"] and result.get("chart_html"):
            chart_html = result["chart_html"]
            
            # Wrap in a complete HTML page for better viewing
            full_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Text2SQL Chart - {request.query[:50]}...</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 20px;
                        padding: 20px;
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .chart-container {{
                        background: white;
                        border-radius: 8px;
                        padding: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .response {{
                        background: #e3f2fd;
                        border-left: 4px solid #2196f3;
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 4px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Text2SQL Chart Visualization</h1>
                    <p><strong>Query:</strong> {request.query}</p>
                </div>
                
                <div class="response">
                    <h3>💬 AI Response:</h3>
                    <p>{result.get('response', 'Chart generated successfully!')}</p>
                </div>
                
                <div class="chart-container">
                    {chart_html}
                </div>
                
                <div style="text-align: center; margin-top: 20px; color: #666;">
                    <p>Generated by Text2SQL API • Interactive chart powered by Plotly</p>
                </div>
            </body>
            </html>
            """
            
            return HTMLResponse(content=full_html, status_code=200)
        else:
            error_message = result.get("error", "No chart was generated for this query")
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Chart Generation Failed</title></head>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>❌ Chart Generation Failed</h2>
                <p><strong>Query:</strong> {request.query}</p>
                <p><strong>Error:</strong> {error_message}</p>
                <p><strong>Tip:</strong> Try queries with chart keywords like 'chart', 'graph', 'plot', 'pie', 'bar', etc.</p>
            </body>
            </html>
            """
            return HTMLResponse(content=error_html, status_code=400)
            
    except Exception as e:
        logger.error(f"Chart view generation failed: {e}")
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>💥 Server Error</h2>
            <p>An error occurred while processing your request.</p>
            <p><strong>Error:</strong> {str(e)}</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)


@router.get("/chart-examples", response_class=HTMLResponse)
async def chart_examples():
    """
    📚 **Chart Examples Gallery**
    
    View example queries that generate different types of charts.
    Click any example to test it directly!
    """
    examples_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Text2SQL Chart Examples</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 12px;
            }
            .examples-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .example-card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .example-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            .chart-type {
                color: #2196f3;
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 10px;
            }
            .query-text {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                margin: 10px 0;
                border-left: 4px solid #2196f3;
            }
            .test-button {
                background: #4caf50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.2s;
            }
            .test-button:hover {
                background: #45a049;
            }
            .api-info {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Text2SQL Chart Examples</h1>
                <p>Try these example queries to see different chart types in action!</p>
            </div>
            
            <div class="examples-grid">
                <div class="example-card">
                    <div class="chart-type">📈 Line Chart</div>
                    <div class="query-text">Show me a line chart of transaction volumes over time</div>
                    <button class="test-button" onclick="testQuery('Show me a line chart of transaction volumes over time')">Test This Query</button>
                </div>
                
                <div class="example-card">
                    <div class="chart-type">📊 Bar Chart</div>
                    <div class="query-text">Create a bar chart of customer balances by income category</div>
                    <button class="test-button" onclick="testQuery('Create a bar chart of customer balances by income category')">Test This Query</button>
                </div>
                
                <div class="example-card">
                    <div class="chart-type">🥧 Pie Chart</div>
                    <div class="query-text">Show me a pie chart of transaction types distribution</div>
                    <button class="test-button" onclick="testQuery('Show me a pie chart of transaction types distribution')">Test This Query</button>
                </div>
                
                <div class="example-card">
                    <div class="chart-type">📈 Scatter Plot</div>
                    <div class="query-text">Generate a scatter plot of income vs credit score</div>
                    <button class="test-button" onclick="testQuery('Generate a scatter plot of income vs credit score')">Test This Query</button>
                </div>
                
                <div class="example-card">
                    <div class="chart-type">📊 Histogram</div>
                    <div class="query-text">Plot a histogram of customer account balances</div>
                    <button class="test-button" onclick="testQuery('Plot a histogram of customer account balances')">Test This Query</button>
                </div>
                
                <div class="example-card">
                    <div class="chart-type">📈 Multi-Series</div>
                    <div class="query-text">Show me charts comparing transaction amounts by channel</div>
                    <button class="test-button" onclick="testQuery('Show me charts comparing transaction amounts by channel')">Test This Query</button>
                </div>
            </div>
            
            <div class="api-info">
                <h3>🔧 API Usage</h3>
                <p><strong>Chart Viewing Endpoint:</strong> <code>POST /api/v1/text2sql/generate-chart</code></p>
                <p><strong>JSON API Endpoint:</strong> <code>POST /api/v1/text2sql/generate</code></p>
                <p><strong>Swagger Documentation:</strong> <a href="/docs" target="_blank">View API Docs</a></p>
            </div>
        </div>
          <script>
            async function testQuery(query) {
                try {
                    // Show loading indicator
                    const button = event.target;
                    const originalText = button.textContent;
                    button.textContent = 'Loading...';
                    button.disabled = true;
                    
                    // Make API request
                    const response = await fetch('/api/v1/text2sql/generate-chart', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query,
                            include_charts: true,
                            max_results: 50
                        })
                    });
                    
                    if (response.ok) {
                        // Open result in new window
                        const htmlContent = await response.text();
                        const newWindow = window.open('', '_blank');
                        newWindow.document.write(htmlContent);
                        newWindow.document.close();
                    } else {
                        alert('Error generating chart. Please try again.');
                    }
                    
                    // Restore button
                    button.textContent = originalText;
                    button.disabled = false;
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error generating chart. Please check console for details.');
                    
                    // Restore button
                    const button = event.target;
                    button.textContent = 'Test This Query';
                    button.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=examples_html, status_code=200)
