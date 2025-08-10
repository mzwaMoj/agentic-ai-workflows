# this script validates and exectues SQL queries against a database.

from pathlib import Path
import sys
import os
src_dir = str(Path(__file__).parent)
sys.path.append(src_dir)

import re
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

try:
    from .sql_connector import connect_to_sql_server
except ImportError:
    # Fallback for when running as script
    try:
        from sql_connector import connect_to_sql_server
    except ImportError:
        print("Error: Could not import connect_to_sql_server. Ensure the sql_connector.py file exists and is correctly implemented.")

def validate_sql_query(query):
    """
    Validates SQL query to ensure it's safe and only contains SELECT statements.
    Returns (is_valid, error_message).
    """
    # Normalize query - remove comments and extra whitespace
    normalized_query = re.sub(r'--.*?(\n|$)', ' ', query)  # Remove line comments
    normalized_query = re.sub(r'/\*.*?\*/', ' ', normalized_query, flags=re.DOTALL)  # Remove block comments
    normalized_query = ' '.join(normalized_query.split())  # Normalize whitespace
    
    # First check if this is a CTE (WITH clause) - if so, it's still a SELECT operation
    if re.match(r'\s*WITH\s+.*?\s+AS\s*\(', normalized_query, re.IGNORECASE):
        # This is a CTE - need to check if it ultimately performs a SELECT
        # Extract the final query part after the last CTE
        cte_parts = re.split(r'\)\s*,?\s*(?:SELECT|WITH)\b', normalized_query, flags=re.IGNORECASE)
        if len(cte_parts) > 1:
            # Check if the final part starts with SELECT
            final_query_part = "SELECT" + cte_parts[-1]
            if not re.search(r'^\s*SELECT\b', final_query_part, re.IGNORECASE):
                return False, "CTEs must end with a SELECT statement"
        else:
            # If we can't parse the CTE structure correctly, look for final SELECT
            if not re.search(r'\)\s*SELECT\b', normalized_query, re.IGNORECASE):
                return False, "CTEs must end with a SELECT statement"
    # If not a CTE, verify it's a regular SELECT
    elif not re.match(r'\s*SELECT\b', normalized_query, re.IGNORECASE):
        return False, "Only SELECT statements are allowed"
    
    # List of dangerous SQL keywords that should be blocked - outside of CTEs and subqueries
    dangerous_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
        'MERGE', 'REPLACE', 'EXEC', 'EXECUTE', 'CALL',
        'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK', 'SAVEPOINT',
        'BACKUP', 'RESTORE', 'SHUTDOWN',
        'OPENROWSET', 'OPENDATASOURCE'
    ]
    
    # More nuanced check for dangerous keywords - check they aren't used as operations
    # rather than just appearing in column/table names
    for keyword in dangerous_keywords:
        # Pattern looks for the keyword followed by whitespace, parenthesis, or semicolon
        # to identify it as a command rather than just part of an identifier
        if re.search(r'\b' + keyword + r'\b\s*[\s\(;]', normalized_query, re.IGNORECASE):
            return False, f"Dangerous SQL keyword detected: {keyword}"
    
    # Check for suspicious patterns that indicate injection attempts
    suspicious_patterns = [
        r';\s*(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)',  # Multiple statements with dangerous operations
        r'UNION.*?(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)',  # Union injection with dangerous operations
        r'--.*;',  # Comment followed by semicolon (potential comment-based SQL injection)
        r'/\*.*?;.*?\*/',  # Block comment containing semicolon
        r'\bXP_\w+\s*\(',  # Extended stored procedures (potential for privilege escalation)
        r'\bSP_\w+\s*\(',  # System stored procedures that might execute dynamic SQL
        r'WAITFOR\s+DELAY',  # Time-based SQL injection technique
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, normalized_query, re.IGNORECASE):
            return False, f"Suspicious SQL pattern detected"
    
    # Additional checks for known SQL injection patterns
    injection_patterns = [
        r"(\bOR|\bAND)\s+['\"]\s*['\"]\s*=",  # OR/AND with empty string comparison
        r"(\bOR|\bAND)\s+\d+\s*=\s*\d+\s+--", # OR/AND with always true condition and comment
        r"'\s*;\s*--",  # Single quote followed by semicolon and comment
        r"'\s*;\s*/\*",  # Single quote followed by semicolon and comment block
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, normalized_query, re.IGNORECASE):
            return False, f"SQL injection pattern detected"
    
    # If a query passes all these checks, it's likely safe
    return True, "Query is valid"


def execute_multiple_sql_code(sql_code, connection=None):
    """
    Accepts a string containing one or more SQL queries, each enclosed in triple backticks.
    Executes each query sequentially and stores the results in a list.
    
    Parameters:
    - sql_code: String containing SQL queries in ```sql code blocks
    - connection: Database connection object (pyodbc connection)
    
    Returns a list of results (SELECT returns DataFrame as JSON, validation errors return error messages).
    """
    
    if connection is None:
        # Try to establish a connection if none is provided
        connection, cursor = connect_to_sql_server()
        
        if connection is None:
            return [{"query": "", "result": "Error: No database connection provided", "status": "connection_error"}]
    
    # Extract SQL queries from code blocks
    queries = re.findall(r'```\s*sql\s*(.*?)```', sql_code, re.DOTALL) or re.findall(r'```(.*?)```', sql_code, re.DOTALL)
    
    if not queries:
        return [{"query": sql_code, 
                "result": "No SQL queries found in the provided code. Please format queries in ```sql code blocks.",
                "status": "format_error"}]
    
    results = []
    
    for query_idx, query in enumerate(queries):
        query = query.strip()
        if not query:
            results.append({
                "query": "", 
                "result": f"Empty query found in code block #{query_idx+1}",
                "status": "validation_error"
            })
            continue
            
        # Validate the query first
        is_valid, validation_message = validate_sql_query(query)
        
        if not is_valid:
            results.append({
                "query": query, 
                "result": f"Query validation failed: {validation_message}",
                "status": "validation_error"
            })
            continue
        
        try:
            print(f"Running Query #{query_idx+1} ______________________")
            print(f"Executing query: {query[:400]}{'...' if len(query) > 100 else ''}")
            print("\n")
            
            # Execute query using pandas read_sql_query
            df = pd.read_sql_query(query, connection)
            
            print(f"Query executed successfully - returned {len(df)} rows with {len(df.columns)} columns")
            
            # Handle results
            result_data = {
                "query": query,
                "status": "success",
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": df.columns.tolist()
            }
            
            # Convert to JSON with error handling
            try:
                result_data["result"] = df.to_json(orient='records', date_format='iso')
            except Exception as json_err:
                result_data["result"] = f"Error converting results to JSON: {str(json_err)}"
                result_data["status"] = "json_error"
                result_data["column_info"] = {col: str(dtype) for col, dtype in df.dtypes.items()}
                
            results.append(result_data)
                
        except Exception as e:
            results.append({
                "query": query, 
                "result": f"Error executing SQL: {str(e)}",
                "status": "execution_error"
            })
    
    return results

def execute_sql_with_pyodbc(sql_code, server=None, database=None, auth_type=None, username=None, password=None):
    """
    Execute SQL queries using pyodbc with the connect_to_sql_server function.
    
    Parameters:
    - sql_code: String containing SQL queries in ```sql code blocks
    - server: Server name (defaults to environment variable)
    - database: Database name (defaults to environment variable)
    - auth_type: Authentication type ('windows' or 'sql')
    - username: SQL Server login username (if using SQL auth)
    - password: SQL Server login password (if using SQL auth)
    
    Returns a list of query results.
    """
    
    # Use connect_to_sql_server to establish a connection
    connection, cursor = connect_to_sql_server(
        server=server,
        database=database,
        auth_type=auth_type,
        username=username,
        password=password
    )
    
    # If no connection could be established
    if connection is None:
        return [{"query": "", 
                "result": "Could not connect to SQL Server. Check server settings and credentials.", 
                "status": "connection_error"}]
    
    # Now process SQL queries
    try:
        # Extract SQL queries from code blocks
        queries = re.findall(r'```\s*sql\s*(.*?)```', sql_code, re.DOTALL) or re.findall(r'```(.*?)```', sql_code, re.DOTALL)
        
        if not queries:
            connection.close()
            return [{"query": sql_code, 
                    "result": "No SQL queries found in the provided code. Please format queries in ```sql code blocks.",
                    "status": "format_error"}]
        
        # Use the existing execute_multiple_sql_code function since it already has all the needed logic
        results = execute_multiple_sql_code(sql_code, connection)
        
        return results
    finally:
        # Ensure connection is closed regardless of success or error
        if connection:
            try:
                # Check if connection is still open before trying to close
                if hasattr(connection, 'connected') and connection.connected:
                    connection.close()
                elif hasattr(connection, 'cursor'):
                    # For pyodbc connections, try to close if not already closed
                    connection.close()
                else:
                    # Fallback: try to close and catch any exceptions
                    connection.close()
            except Exception:
                # Connection might already be closed, ignore the error
                pass

# example usage
if __name__ == "__main__":
    # Example SQL code with multiple queries
    sql_code = """
    ```sql
    SELECT top 10 * 
    FROM [master].[dbo].[transaction_history] WITH (NOLOCK);
    ```
    
    ```sql
    SELECT COUNT(*) FROM [master].[dbo].[transaction_history] WITH (NOLOCK);
    ```
    
    ```sql
    SELECT TOP 100 * 
    FROM [master].[dbo].[customer_information] WITH (NOLOCK);
    ```    """
    
    results = execute_sql_with_pyodbc(sql_code)
    
    for result in results:
        print(f"Query: {result['query']}")
        # print(f"Result: {result['result']}")
        print(f"Status: {result['status']}")
        print("-" * 50)
        print("\n\n")

