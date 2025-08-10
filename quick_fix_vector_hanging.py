"""
Quick fix for the hanging vector issue.
Replace the _agent_table_retriever method with a version that returns mock data.
"""

def get_mock_table_metadata():
    """Return mock table metadata to bypass vector search hanging."""
    return """
Table: customer_information
Columns:
- customer_id (int, primary key): Unique identifier for each customer
- first_name (varchar): Customer's first name
- last_name (varchar): Customer's last name  
- email (varchar): Customer's email address
- phone (varchar): Customer's phone number
- address (varchar): Customer's address
- city (varchar): Customer's city
- state (varchar): Customer's state
- zip_code (varchar): Customer's zip code
- account_balance (decimal): Customer's current account balance
- account_type (varchar): Type of account (checking, savings, etc.)
- date_created (datetime): When the customer account was created

Table: transaction_history  
Columns:
- transaction_id (int, primary key): Unique identifier for each transaction
- customer_id (int, foreign key): References customer_information.customer_id
- transaction_date (datetime): When the transaction occurred
- transaction_type (varchar): Type of transaction (deposit, withdrawal, transfer, etc.)
- amount (decimal): Transaction amount
- description (varchar): Description of the transaction
- balance_after (decimal): Account balance after the transaction
""".strip()

# Replacement method for text2sql_engine.py
def _agent_table_retriever_mock(self, user_request: str, agent_table_router):
    """
    Mock table retriever that bypasses vector search to prevent hanging.
    """
    import json
    
    try:
        # Get response from table router (following chatbot.py)
        response = agent_table_router(user_request)
        
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name == "agent_table_rag":
            args = json.loads(tool_call.function.arguments)
            
            # Log the required tables
            try:
                from app.utils import log_required_tables
                log_required_tables(args.get("relevant_tables"))
            except ImportError:
                pass
            
            # Return mock data instead of calling vector search
            result = get_mock_table_metadata()
            logger.info(f"Returning mock table metadata (length: {len(result)})")
            return result
            
        else:
            logger.warning(f"Unexpected tool call name: {tool_call.function.name}")
            return get_mock_table_metadata()
    
    except Exception as e:
        logger.error(f"Table router failed: {e}")
        return get_mock_table_metadata()

if __name__ == "__main__":
    print("Mock table metadata method ready to replace hanging vector search.")
    print("Length:", len(get_mock_table_metadata()))
