# Lesson 4: Text-to-SQL RAG Agent

This lesson teaches you how to build an AI agent that can convert natural language queries into SQL and execute them against a database. You'll learn to create a complete text-to-SQL solution using SQLite and OpenAI's function calling capabilities.

## Learning Objectives

By the end of this lesson, you will be able to:

1. Convert natural language queries to SQL using LLMs
2. Create and query SQLite databases from CSV data
3. Build text-to-SQL agents with function calling
4. Implement safety measures for SQL execution
5. Handle complex multi-table queries with proper table schema understanding
6. Create a conversational database interface

## Files in this lesson

- `lesson_4_notebook.ipynb` - Main tutorial notebook
- `create_dummy_data.py` - Script to generate sample e-commerce data
- `sample_database.sqlite` - SQLite database with sample data
- `examples/example_4.py` - Basic text-to-SQL examples
- `exercises/exercise_4.py` - Practice exercises

## Prerequisites

- Basic SQL knowledge
- Understanding of database schemas and relationships
- Familiarity with Python and pandas
- OpenAI API access (Azure OpenAI or OpenAI)

## Setup

1. Install required packages:
```bash
pip install faker pandas sqlite3 openai python-dotenv
```

2. Generate sample data:
```bash
python create_dummy_data.py
```

3. Set up your environment variables in `.env`:
```
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_VERSION=your_api_version
AZURE_OPENAI_MODEL=your_model_name
```

## Database Schema

The sample database contains 5 tables representing an e-commerce system:

- **customers**: Customer information (ID, name, email, address, etc.)
- **products**: Product catalog (ID, name, category, price, stock, etc.)
- **orders**: Order information (ID, customer_id, date, status, total, etc.)
- **order_items**: Individual items in orders (order_id, product_id, quantity, price)
- **reviews**: Product reviews (customer_id, product_id, rating, text, date)

## Key Features

### 1. Data Generation
- Uses Faker library to create realistic sample data
- Generates 1000+ customers, 200+ products, 2000+ orders
- Creates proper relationships between tables

### 2. Database Operations
- SQLite database creation from CSV files
- Safe SQL query execution with result limiting
- Schema introspection and validation

### 3. Text-to-SQL Conversion
- Basic prompting for SQL generation
- Schema-aware query generation
- Proper JOIN handling for multi-table queries

### 4. Function Calling Agent
- OpenAI function calling for dynamic query execution
- Natural language response generation
- Error handling and recovery

### 5. Conversational Interface
- Context-aware conversations
- Multi-turn query refinement
- History management

### 6. Safety Features
- SQL injection prevention
- Query validation (read-only operations)
- Result set limiting
- Error handling and user feedback

## Example Queries

### Basic Queries:
- "Show me all customers"
- "What products do we have?"
- "How many orders were placed today?"

### Analytics:
- "What's our total revenue?"
- "Which products are bestsellers?"
- "What's the average order value?"
- "Show me sales by month"

### Complex Queries:
- "Show customers who have never placed an order"
- "What products have the highest ratings?"
- "Find customers from California who bought Electronics"
- "Show me orders with more than 3 items"

## Architecture

```
User Query → LLM (Text-to-SQL) → SQL Validation → Database Execution → Results → LLM (Response Generation) → Natural Language Response
```

## Safety Note

When building text-to-SQL systems:
- Always validate SQL queries before execution
- Use read-only database connections when possible
- Implement query timeouts
- Sanitize user inputs
- Consider using SQL query whitelisting for production systems

## Next Steps

1. **Add more data sources**: Integrate with other databases or APIs
2. **Improve error handling**: Add more sophisticated query correction
3. **Add caching**: Cache frequent queries for better performance
4. **Enhance security**: Implement user authentication and access controls
5. **Add visualizations**: Create charts and graphs from query results
6. **Deploy as API**: Create a REST API for the text-to-SQL service

## Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [SQL Best Practices](https://www.sqlstyle.guide/)
- [Database Design Principles](https://en.wikipedia.org/wiki/Database_design)
