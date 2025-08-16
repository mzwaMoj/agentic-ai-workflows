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
        # If no code blocks found, try to clean the entire sql_code and treat it as a single query
        # This handles cases where LLM generates SQL with markdown headers but no code blocks
        cleaned_code = clean_sql_query(sql_code)
        if cleaned_code and cleaned_code.strip():
            queries = [cleaned_code]
        else:
            return [{"query": sql_code, 
                    "result": "No SQL queries found in the provided code. Please format queries in ```sql code blocks.",
                    "status": "format_error"}]
    results = []
    
    for query_idx, query in enumerate(queries):
        query = query.strip()
        
        # Clean the query to remove markdown headers and LLM-generated content
        query = clean_sql_query(query)
        
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

def clean_sql_query(query):
    """
    Cleans up SQL query by removing LLM-generated markdown headers and other 
    problematic text that might break SQL execution, while preserving valid SQL comments.
    
    Parameters:
    - query: String containing the raw SQL query with potential markdown/comments
    
    Returns:
    - cleaned_query: String containing the cleaned SQL query
    """
    if not query or not isinstance(query, str):
        return query
    
    # Remove markdown headers (## SQL Query, # Query, etc.) but preserve SQL line comments (--)
    cleaned_query = re.sub(r'^#+\s*.*$', '', query, flags=re.MULTILINE)
    
    # Remove markdown code block indicators if they exist outside of our expected format
    cleaned_query = re.sub(r'^```\s*sql\s*$', '', cleaned_query, flags=re.MULTILINE)
    cleaned_query = re.sub(r'^```\s*$', '', cleaned_query, flags=re.MULTILINE)
    
    # Remove numbered list prefixes (1. Customer base chart, 2. Analysis, etc.)
    # But only if they don't look like SQL content
    cleaned_query = re.sub(r'^\s*\d+\.\s+[^S][^E][^L].*$', '', cleaned_query, flags=re.MULTILINE | re.IGNORECASE)
    
    # Remove bullet point prefixes (- Query, * Analysis, etc.) but not SQL operators
    # Only remove lines that start with bullet points followed by descriptive text
    cleaned_query = re.sub(r'^\s*[-*]\s+(?!.*SELECT|.*FROM|.*WHERE|.*GROUP|.*ORDER).*$', '', cleaned_query, flags=re.MULTILINE | re.IGNORECASE)
    
    # Remove common LLM explanatory text patterns that are clearly not SQL
    explanatory_patterns = [
        r'^\s*Here\s+is\s+the\s+.*query.*:?\s*$',
        r'^\s*The\s+following\s+query.*:?\s*$',
        r'^\s*This\s+query.*:?\s*$',
        r'^\s*Query\s+explanation.*:?\s*$',
        r'^\s*SQL\s+Query.*:?\s*$',
        r'^\s*Analysis.*:?\s*$',
        r'^\s*Chart.*:?\s*$',
        r'^\s*Report.*:?\s*$',
        r'^\s*Explanation.*:?\s*$',
        r'^\s*Description.*:?\s*$',
    ]
    
    for pattern in explanatory_patterns:
        cleaned_query = re.sub(pattern, '', cleaned_query, flags=re.MULTILINE | re.IGNORECASE)
    
    # Remove lines that are clearly prose/explanation but preserve SQL comments
    # Look for lines that contain common English words but don't contain SQL keywords
    prose_patterns = [
        r'^\s*(?!--).*\b(?:will|shows?|gives?|returns?|provides?|analysis|breakdown|complete)\b.*(?<!;)\s*$',
        r'^\s*(?!--).*\b(?:This|That|These|Those)\s+.*(?<!;)\s*$',
    ]
    
    for pattern in prose_patterns:
        # Only remove if the line doesn't contain SQL keywords
        if not re.search(r'\b(?:SELECT|FROM|WHERE|GROUP|ORDER|JOIN|UNION|INSERT|UPDATE|DELETE)\b', cleaned_query, re.IGNORECASE):
            cleaned_query = re.sub(pattern, '', cleaned_query, flags=re.MULTILINE | re.IGNORECASE)
    
    # Remove empty lines and normalize whitespace
    cleaned_query = re.sub(r'\n\s*\n', '\n', cleaned_query)  # Remove multiple empty lines
    cleaned_query = re.sub(r'^\s*\n', '', cleaned_query)     # Remove leading empty lines
    cleaned_query = re.sub(r'\n\s*$', '', cleaned_query)     # Remove trailing empty lines
    
    # Final cleanup - strip leading/trailing whitespace
    cleaned_query = cleaned_query.strip()
    
    return cleaned_query

def test_sql_cleaning():
    """
    Test function to demonstrate SQL query cleaning functionality.
    """
    print("Testing SQL Query Cleaning Function")
    print("=" * 50)
    
    # Test case 1: Query with markdown headers
    problematic_query1 = """
-- 1. Customer base chart by account type and age group (age binning)
## SQL Query
SELECT 
    account_type,
    CASE 
        WHEN age BETWEEN 18 AND 25 THEN '18-25'
        WHEN age BETWEEN 26 AND 35 THEN '26-35'
        WHEN age BETWEEN 36 AND 45 THEN '36-45'
        WHEN age BETWEEN 46 AND 55 THEN '46-55'
        WHEN age BETWEEN 56 AND 65 THEN '56-65'
        WHEN age > 65 THEN '66-75'
        ELSE 'Unknown'
    END AS age_group,
    COUNT(*) AS customer_count
FROM [master].[dbo].[customer_information] WITH (NOLOCK)
GROUP BY 
    account_type,
    CASE 
        WHEN age BETWEEN 18 AND 25 THEN '18-25'
        WHEN age BETWEEN 26 AND 35 THEN '26-35'
        WHEN age BETWEEN 36 AND 45 THEN '36-45'
        WHEN age BETWEEN 46 AND 55 THEN '46-55'
        WHEN age BETWEEN 56 AND 65 THEN '56-65'
        WHEN age > 65 THEN '66-75'
        ELSE 'Unknown'
    END
ORDER BY account_type, age_group;
"""
    
    cleaned1 = clean_sql_query(problematic_query1)
    print("Test Case 1: Query with markdown headers")
    print("Original query (first 200 chars):", repr(problematic_query1[:200]))
    print("Cleaned query (first 200 chars):", repr(cleaned1[:200]))
    print("Validation result:", validate_sql_query(cleaned1))
    print()
    
    # Test case 2: Query with numbered list and explanatory text
    problematic_query2 = """
1. Transaction analysis report
Here is the SQL query to analyze transactions:

## Query
SELECT transaction_type, COUNT(*) as count 
FROM [master].[dbo].[transaction_history] WITH (NOLOCK)
GROUP BY transaction_type;

This query will give us the transaction breakdown.
"""
    
    cleaned2 = clean_sql_query(problematic_query2)
    print("Test Case 2: Query with numbered list and explanatory text")
    print("Original query:", repr(problematic_query2))
    print("Cleaned query:", repr(cleaned2))
    print("Validation result:", validate_sql_query(cleaned2))
    print()
    
    # Test case 3: Multiple formatting issues
    problematic_query3 = """
# Customer Report Analysis
* This query analyzes customer data
The following query shows customer information:

```sql
SELECT TOP 50 * FROM [master].[dbo].[customer_information] WITH (NOLOCK);
```

Analysis complete.
"""
    
    cleaned3 = clean_sql_query(problematic_query3)
    print("Test Case 3: Multiple formatting issues")
    print("Original query:", repr(problematic_query3))
    print("Cleaned query:", repr(cleaned3))
    print("Validation result:", validate_sql_query(cleaned3))
    print()

# example usage
if __name__ == "__main__":
    # Test the SQL cleaning function
    test_sql_cleaning()
    
    print("\n" + "="*50)
    print("Running actual SQL execution test...")
    print("="*50)
    
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

