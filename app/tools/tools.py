# Tool definitions for Azure OpenAI API with proper schema

# SQL Analysis Tool
tool_sql_analysis = {
    "type": "function",
    "function": {
        "name": "agent_sql_analysis",
        "description": (
            "multi-intent sql analysis. Generates executable Microsoft SQL Server (MSSQL) queries based on user requests for database operations. "
            "The 'user_requests' parameter can be any data type (string, list, dictionary, tuple, JSON object, etc.), "
            "including natural language, structured instructions, or outputs from other agents. "
            "The function can handle complex queries involving multiple tables, aggregations, and conditions."
            "The function should interpret the intent or intents and generate an appropriate SQL query."
            
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_requests": {
                    "type": "string", 
                    "description": (
                        "The user's request/s, which can be any data type (string, list, dictionary, tuple, JSON object, etc.), "
                        "including natural language, structured input, or the output from the router agent about what database operation to perform."
                        "user request can be multiple intents or single intents."
                        "Multi-intent Example: 1. What is my account balance? 2. How much loan do I qualify for? Here is my id: 12345. "
                    )
                },
                "identifier": {
                    "type": "string",
                    "description": "Optional: The customer ID or account number if specified in the request"
                }
            },
            "required": ["user_requests"]
        }

    }
}

tool_table_retriever = {
    "type": "function",
    "function": {
        "name": "agent_table_retriever",
        "description": (
            "Identifies the necessary database tables that contain information relevant to solving a user query. "
            "The 'user_requests' parameter can be any data type (string, list, dictionary, tuple, JSON object, etc.), "
            "This tool acts as a router, directing subsequent operations to the correct data sources. "
            "The output will be a list of table names identified as relevant."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_request": {
                    "type": "string", 
                    "description": (
                        "The user's natural language query. This tool will process this request "
                        "to determine which database tables are most relevant for answering it. "
                        "Examples: 'loan data', 'transaction history', 'customer balance'."
                    )
                },
                "identifier": {
                    "type": "string",
                    "description": "Optional: The customer ID or account number if specified in the request."
                }
            },
            "required": ["user_request"]
        }
    }
}
tool_table_rag = {
    "type": "function",
    "function": {
        "name": "agent_table_rag",
        "description": (
            "Identifies the necessary database tables that contain information relevant to solving a user query. "
            "The 'user_requests' parameter can be any data type (string, list, dictionary, tuple, JSON object, etc.), "
            "The output will be a list of table names identified as relevant."
            "Examples: ['customer_information', 'transaction_history']. "
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "relevant_tables": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": (
                        "A list of table names identified as relevant to the user's query. "
                        "The table names can be single table or multiple tables. "
                        " for example, single user intent with a single table: ['customer_information']"
                        "for example, multiple intents: Which quarter had the highest amount and the lowest amount? Which client has the lowest and highest balance? Output:  relevant_tables: [customer_information, transaction_history]"
                    )
                },
                "original_user_query": {
                    "type": "string",
                    "description": "The original natural language query from the user that triggered the table identification."
                }
            },
            "required": ["relevant_tables"]
        }
    }
}

tool_generate_charts = {
    "type": "function",
    "function": {
        "name": "agent_generate_charts",
        "description": (
            "Generates Python code to create one or more charts based on user input. "
            "This tool accepts a wide range of input formats including natural language, structured data (JSON, dicts), "
            "or lists of chart specifications. It supports multiple chart types such as bar charts, line graphs, pie charts, "
            "scatter plots, histograms, and more. The generated code is parsed and executed to produce the requested visualizations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_request": {
                    "type": "string",
                    "description": (
                        "The user's request describing the desired chart(s). This can include chart types, data to be visualized, "
                        "labels, titles, and other customization options. The input may be in natural language or structured format. "
                        "Examples: 'Plot a bar chart of sales by region', 'Show a line graph of temperature over time', "
                        "'Create a pie chart and a histogram from this dataset'."
                    )
                },
                "identifier": {
                    "type": "string",
                    "description": "Optional: A unique identifier for the chart request, such as a dataset name or user session ID."
                }
            },
            "required": ["user_request"]
        }
    }
}




tools = [ tool_sql_analysis, tool_table_rag]

def tools_definitions():
    """
    Defines the available tools (functions) for the language model
    in the latest OpenAI API format.

    Returns:
        list: A list of tool definitions, each structured for the API.
    """
    return tools
