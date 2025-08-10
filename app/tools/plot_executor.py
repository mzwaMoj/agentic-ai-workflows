import sys
import os
import io
import ast
import traceback
import pandas as pd
import numpy as np
from PIL import Image
import base64
from IPython.display import HTML, display
import time

# Import from app.db module
from app.db import connect_to_sql_server

# Import plotly libraries
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Global DataFrames to store preloaded data
customer_df = None
transaction_df = None
last_data_refresh = 0
DATA_REFRESH_INTERVAL = 300  # Refresh data every 5 minutes

def load_data_tables(force_reload=False, server=None, database=None, auth_type='windows', username=None, password=None):
    """
    Load both customer and transaction tables into memory.
    Data is cached and only reloaded if force_reload is True or if the cache is older than DATA_REFRESH_INTERVAL.
    
    Args:
        force_reload (bool): If True, force reloading the data even if cached
        server, database, auth_type, username, password: Parameters passed to connect_to_sql_server
        
    Returns:
        tuple: (customer_df, transaction_df) - DataFrames containing the table data
    """
    global customer_df, transaction_df, last_data_refresh
    
    # Check if we need to refresh the data
    current_time = time.time()
    if (not force_reload and 
        customer_df is not None and 
        transaction_df is not None and 
        current_time - last_data_refresh < DATA_REFRESH_INTERVAL):
        print(f"Using cached data (last refresh: {int((current_time - last_data_refresh)/60)} minutes ago)")
        return customer_df, transaction_df
    
    # Connect to the database
    conn, cursor = connect_to_sql_server(
        server=server, 
        database=database, 
        auth_type=auth_type,
        username=username,
        password=password
    )
    
    if conn is None or cursor is None:
        print("Failed to connect to the database. Using cached data if available.")
        if customer_df is not None and transaction_df is not None:
            return customer_df, transaction_df
        return None, None
    
    try:
        print("Loading customer information table...")
        customer_query = "SELECT * FROM [master].[dbo].[customer_information]"
        customer_df = pd.read_sql(customer_query, conn)
        print(f"Loaded {len(customer_df)} customer records with columns: {', '.join(customer_df.columns)}")
        
        print("Loading transaction history table...")
        transaction_query = "SELECT * FROM [master].[dbo].[transaction_history]"
        transaction_df = pd.read_sql(transaction_query, conn)
        
        # Convert transaction_date to datetime
        if 'transaction_date' in transaction_df.columns:
            transaction_df['transaction_date'] = pd.to_datetime(transaction_df['transaction_date'])
            
        print(f"Loaded {len(transaction_df)} transaction records with columns: {', '.join(transaction_df.columns)}")
        
        # Update the refresh timestamp
        last_data_refresh = current_time
        
        # Close the connection
        cursor.close()
        conn.close()
        print("Database connection closed")
        
        return customer_df, transaction_df
        
    except Exception as e:
        print(f"Error loading data tables: {str(e)}")
        traceback.print_exc()
        
        # Close the connection if it was opened
        if conn and cursor:
            cursor.close()
            conn.close()
            print("Database connection closed after error")
        
        # Return cached data if available
        if customer_df is not None and transaction_df is not None:
            print("Using cached data due to error")
            return customer_df, transaction_df
        
        return None, None

def fetch_data_from_db(query, server=None, database=None, auth_type='windows', username=None, password=None):
    """
    Fetch data from the database using the provided SQL query.
    
    Args:
        query (str): SQL query to execute
        server, database, auth_type, username, password: Parameters passed to connect_to_sql_server
        
    Returns:
        pandas.DataFrame: DataFrame containing the query results or None if the query fails
    """
    try:
        # Connect to the database
        conn, cursor = connect_to_sql_server(
            server=server, 
            database=database, 
            auth_type=auth_type,
            username=username,
            password=password
        )
        
        if conn is None or cursor is None:
            print("Failed to connect to the database")
            return None
            
        print(f"Executing query: {query[:100]}...")  # Print first 100 chars of query for logging
        
        # Execute the query and fetch data into a pandas DataFrame
        df = pd.read_sql(query, conn)
        
        # Close the connection
        cursor.close()
        conn.close()
        
        print(f"Query successful. Fetched {len(df)} rows with columns: {', '.join(df.columns)}")
        return df
        
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        traceback.print_exc()
        return None

def execute_plot_code(code, df=None, height=800, width=1000, use_preloaded_data=True):
    """
    Execute the generated Python code and return the interactive Plotly visualization.
    
    Args:
        code (str): Python code to execute (should use Plotly for visualization)
        df (pandas.DataFrame, optional): Custom DataFrame to use in the visualization
        height (int): Height of the plot in pixels
        width (int): Width of the plot in pixels
        use_preloaded_data (bool): Whether to make preloaded data available in the execution context
        
    Returns:
        str: HTML string of the interactive plot, or error message
    """
    global customer_df, transaction_df
    
    # Load data if needed and not provided
    if use_preloaded_data and (customer_df is None or transaction_df is None):
        load_data_tables()
    
    try:
        # Clean the code (remove markdown code block syntax if present)
        if "```python" in code:
            code = code.strip().split("```python", 1)[1]
        if "```" in code:
            code = code.split("```", 1)[0]
        code = code.strip()
        
        # Parse the input code
        parsed_code = ast.parse(code)
        
        # Create a safe execution environment with necessary libraries
        exec_globals = {
            "pd": pd,
            "np": np,
            "px": px,
            "go": go,
            "make_subplots": make_subplots,
            "plt": None  # In case code references plt but doesn't use it
        }
        
        # Add the dataframes to the execution environment
        if df is not None:
            exec_globals["df"] = df
        
        if use_preloaded_data:
            if customer_df is not None:
                exec_globals["customer_df"] = customer_df
            if transaction_df is not None:
                exec_globals["transaction_df"] = transaction_df
        
        # Execute the code with the dataframe(s)
        exec(compile(parsed_code, filename="<ast>", mode="exec"), exec_globals)
        
        # Look for a figure object in the execution environment
        fig = None
        for var_name, var_value in exec_globals.items():
            if var_name != "df" and var_name != "pd" and var_name != "np" and var_name != "px" and var_name != "go" and var_name != "make_subplots" and var_name != "plt":
                if hasattr(var_value, 'update_layout'):  # It's likely a Plotly figure
                    fig = var_value
                    break
        
        # If no figure found, check for a 'fig' variable specifically
        if fig is None and 'fig' in exec_globals:
            fig = exec_globals['fig']
        
        # If still no figure found, return an error
        if fig is None:
            return "Error: No Plotly figure object found in the executed code. Make sure your code creates a figure named 'fig'."
        
        # Update the figure layout with the specified dimensions
        fig.update_layout(
            height=height,
            width=width,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        # Convert the figure to HTML
        html_str = fig.to_html(include_plotlyjs='cdn', full_html=False)
        return html_str
        
    except SyntaxError as e:
        return f"Syntax Error: {str(e)}"
    except Exception as e:
        traceback.print_exc()
        return f"Error executing code: {str(e)}"

def display_plot(html_content):
    """
    Display the HTML plot in a Jupyter notebook or return the HTML content.
    
    Args:
        html_content (str): HTML string containing the Plotly visualization
        
    Returns:
        str or None: HTML string if not in a Jupyter environment, else None after displaying
    """
    try:
        # Try to display in Jupyter notebook
        display(HTML(html_content))
        return None
    except:
        # Return HTML content if not in a Jupyter environment
        return html_content

def save_plot_to_image(code, df=None, filename="plot.png", format="png", height=800, width=1000, use_preloaded_data=True):
    """
    Execute the plot code and save the resulting visualization as an image file.
    
    Args:
        code (str): Python code to execute
        df (pandas.DataFrame, optional): Custom DataFrame to use in the visualization
        filename (str): Name of the output file
        format (str): Image format (png, jpg, svg, pdf)
        height (int): Height of the plot in pixels
        width (int): Width of the plot in pixels
        use_preloaded_data (bool): Whether to make preloaded data available in the execution context
        
    Returns:
        str: Path to the saved image or error message
    """
    global customer_df, transaction_df
    
    # Load data if needed and not provided
    if use_preloaded_data and (customer_df is None or transaction_df is None):
        load_data_tables()
    
    try:
        # Clean the code (remove markdown code block syntax if present)
        if "```python" in code:
            code = code.strip().split("```python", 1)[1]
        if "```" in code:
            code = code.split("```", 1)[0]
        code = code.strip()
        
        # Parse the input code
        parsed_code = ast.parse(code)
        
        # Create a safe execution environment with necessary libraries
        exec_globals = {
            "pd": pd,
            "np": np,
            "px": px, 
            "go": go,
            "make_subplots": make_subplots,
            "plt": None
        }
        
        # Add the dataframes to the execution environment
        if df is not None:
            exec_globals["df"] = df
        
        if use_preloaded_data:
            if customer_df is not None:
                exec_globals["customer_df"] = customer_df
            if transaction_df is not None:
                exec_globals["transaction_df"] = transaction_df
        
        # Execute the code with the dataframe(s)
        exec(compile(parsed_code, filename="<ast>", mode="exec"), exec_globals)
        
        # Look for a figure object in the execution environment
        fig = None
        for var_name, var_value in exec_globals.items():
            if var_name != "df" and var_name != "pd" and var_name != "np" and var_name != "px" and var_name != "go" and var_name != "make_subplots" and var_name != "plt":
                if hasattr(var_value, 'update_layout'):  # It's likely a Plotly figure
                    fig = var_value
                    break
        
        # If no figure found, check for a 'fig' variable specifically
        if fig is None and 'fig' in exec_globals:
            fig = exec_globals['fig']
        
        # If still no figure found, return an error
        if fig is None:
            return "Error: No Plotly figure object found in the executed code. Make sure your code creates a figure named 'fig'."
        
        # Update the figure layout with the specified dimensions
        fig.update_layout(
            height=height,
            width=width,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        # Save the figure to the specified format
        pio.write_image(fig, filename, format=format, scale=2)  # scale=2 for better resolution
        
        print(f"Plot saved to {filename}")
        return filename
        
    except Exception as e:
        traceback.print_exc()
        return f"Error saving plot: {str(e)}"

def example_usage():
    """
    Example of how to use the plot executor functions.
    """
    # Preload data tables
    print("Preloading data tables...")
    customer_data, transaction_data = load_data_tables()
    
    if customer_data is None or transaction_data is None:
        print("Failed to load one or both data tables. Cannot proceed with visualization.")
        return
    
    print("\n==== EXAMPLE 1: Using preloaded customer data ====")
    
    # Example Plotly code for a bar chart using customer data
    customer_example_code = """
    import plotly.express as px
    
    # Group data by income_category
    if 'income_category' in customer_df.columns:
        grouped_data = customer_df.groupby('income_category')['income'].sum().reset_index()
        
        # Create a bar chart
        fig = px.bar(
            grouped_data,
            x='income_category',
            y='income',
            title='Total Income by Category',
            labels={'income_category': 'Income Category', 'income': 'Total Income'},
            color='income_category'
        )
        
        # Add formatting
        fig.update_layout(
            xaxis_title='Income Category',
            yaxis_title='Total Income ($)',
            yaxis_tickprefix='$',
            legend_title='Category'
        )
    else:
        # If income_category doesn't exist, create a simple bar chart of another column
        fig = px.bar(
            customer_df,
            x=customer_df.columns[0],  # Use first column as x-axis
            y=customer_df.columns[1] if len(customer_df.columns) > 1 else customer_df.columns[0],  # Use second column as y-axis if available
            title='Sample Data Visualization',
        )
    """
    
    # Execute the code and get the interactive HTML
    html_plot = execute_plot_code(customer_example_code)
    
    # Display the plot
    print("To display the plot in a notebook, use:")
    print("display_plot(html_plot)")
    
    # Save the plot as an image
    save_plot_to_image(customer_example_code, filename="customer_example_plot.png")
    
    print("\n==== EXAMPLE 2: Using preloaded transaction data ====")
    
    # Example Plotly code for a line chart using transaction data
    transaction_example_code = """
    import plotly.express as px
    
    # Ensure transaction_date is in datetime format
    if 'transaction_date' in transaction_df.columns:
        # Group by date and calculate daily transaction totals
        daily_transactions = transaction_df.groupby(
            pd.Grouper(key='transaction_date', freq='D')
        )['amount'].sum().reset_index()
        
        # Create a line chart
        fig = px.line(
            daily_transactions,
            x='transaction_date',
            y='amount',
            title='Daily Transaction Amounts',
            labels={'transaction_date': 'Date', 'amount': 'Total Amount'}
        )
        
        # Add formatting
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Transaction Amount ($)',
            yaxis_tickprefix='$'
        )
        
        # Add range slider
        fig.update_xaxes(rangeslider_visible=True)
    else:
        # Fallback if transaction_date doesn't exist
        fig = px.scatter(
            transaction_df,
            x=transaction_df.columns[0],
            y=transaction_df.columns[1] if len(transaction_df.columns) > 1 else transaction_df.columns[0],
            title='Sample Transaction Data Visualization'
        )
    """
    
    # Execute the code and get the interactive HTML
    html_plot = execute_plot_code(transaction_example_code)
    
    # Save the plot as an image
    save_plot_to_image(transaction_example_code, filename="transaction_example_plot.png")
    
    print("\n==== EXAMPLE 3: Using custom query data ====")
    
    # Custom query example
    custom_query = """
    SELECT TOP 50 * 
    FROM [master].[dbo].[customer_information]
    WHERE income > 50000
    """
    
    # Fetch custom data
    custom_df = fetch_data_from_db(custom_query)
    
    if custom_df is not None:
        # Example code using custom data
        custom_example_code = """
        import plotly.express as px
        
        # Create a scatter plot
        fig = px.scatter(
            df,  # This is the custom dataframe from fetch_data_from_db
            x='credit_score',
            y='income',
            color='income_category',
            size='balance',
            title='Credit Score vs Income (High Income Customers)',
            labels={
                'credit_score': 'Credit Score', 
                'income': 'Annual Income', 
                'income_category': 'Income Category',
                'balance': 'Account Balance'
            }
        )
        
        fig.update_layout(
            yaxis_tickprefix='$',
            height=600
        )
        """
        
        # Execute with custom data
        html_plot = execute_plot_code(custom_example_code, custom_df, use_preloaded_data=False)
        save_plot_to_image(custom_example_code, custom_df, "custom_example_plot.png", use_preloaded_data=False)
    
    print("\nTo use this module in another script:")
    print("from tools.plot_executor import load_data_tables, execute_plot_code, display_plot")
    print("\n# Method 1: Using preloaded data")
    print("load_data_tables()  # Load data once at the start")
    print("html_plot = execute_plot_code(code_string)  # Uses preloaded data")
    print("display_plot(html_plot)")
    print("\n# Method 2: Using custom query data")
    print("from tools.plot_executor import fetch_data_from_db")
    print("custom_df = fetch_data_from_db('SELECT * FROM table')")
    print("html_plot = execute_plot_code(code_string, custom_df)")
    print("display_plot(html_plot)")

def initialize(server=None, database=None, auth_type='windows', username=None, password=None):
    """
    Initialize the plot executor by loading data tables.
    Call this function once when starting your application to preload data.
    
    Args:
        server, database, auth_type, username, password: Parameters passed to connect_to_sql_server
        
    Returns:
        tuple: (customer_df, transaction_df) - DataFrames containing the table data
    """
    return load_data_tables(force_reload=True, 
                           server=server, 
                           database=database, 
                           auth_type=auth_type, 
                           username=username, 
                           password=password)

if __name__ == "__main__":
    example_usage()
