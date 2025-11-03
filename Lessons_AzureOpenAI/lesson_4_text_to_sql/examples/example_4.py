"""
Example 4: Basic Text-to-SQL Implementation

This example demonstrates a simple text-to-SQL conversion using OpenAI
and SQLite database operations.
"""

import sqlite3
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_KEY"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.environ.get("AZURE_OPENAI_VERSION"),
)

MODEL = os.environ.get("AZURE_OPENAI_MODEL")

def get_database_schema():
    """Get database schema information"""
    conn = sqlite3.connect('sample_database.sqlite')
    cursor = conn.cursor()
    
    schema_info = ""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        schema_info += f"\nTable: {table_name}\n"
        
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        for col in columns:
            schema_info += f"  - {col[1]} ({col[2]})\n"
    
    conn.close()
    return schema_info

def text_to_sql(question):
    """Convert natural language question to SQL"""
    
    schema = get_database_schema()
    
    prompt = f"""Convert the following question to a SQL query.

Database Schema:
{schema}

Question: {question}

Generate only the SQL query, no explanations:"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a SQL expert. Generate only valid SQLite queries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=200
    )
    
    sql_query = response.choices[0].message.content.strip()
    
    # Clean up response
    if sql_query.startswith('```sql'):
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
    elif sql_query.startswith('```'):
        sql_query = sql_query.replace('```', '').strip()
        
    return sql_query

def execute_query(sql_query):
    """Execute SQL query and return results"""
    try:
        conn = sqlite3.connect('sample_database.sqlite')
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        
        conn.close()
        
        return {
            'success': True,
            'results': results,
            'columns': column_names
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Main function to demonstrate text-to-SQL"""
    
    # Example questions
    questions = [
        "How many customers are there?",
        "Show me the top 5 most expensive products",
        "What is the total revenue from all orders?",
        "Which customers are from California?"
    ]
    
    for question in questions:
        print(f"\n{'='*50}")
        print(f"Question: {question}")
        
        # Convert to SQL
        sql_query = text_to_sql(question)
        print(f"Generated SQL: {sql_query}")
        
        # Execute query
        result = execute_query(sql_query)
        
        if result['success']:
            print(f"Results ({len(result['results'])} rows):")
            print(f"Columns: {result['columns']}")
            
            # Show first few results
            for i, row in enumerate(result['results'][:5]):
                print(f"  Row {i+1}: {row}")
                
            if len(result['results']) > 5:
                print(f"  ... and {len(result['results']) - 5} more rows")
        else:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
