import pyodbc
import os
import platform
import dotenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def connect_to_sql_server(server=None, database=None, auth_type='windows', username=None, password=None):
    """
    Connect to SQL Server using authentication fallback for the specified server and database.
    Supports both Windows and macOS platforms.
    
    Args:
        server (str): SQL Server instance name
        database (str): Database name
        auth_type (str): Preferred authentication type ('windows' or 'sql')
        username (str, optional): SQL Server login username
        password (str, optional): SQL Server login password
        
    Returns:
        tuple: (connection_object, cursor_object) or (None, None) if all connections fail
    """
    
    # Detect platform
    current_platform = platform.system().lower()
    
    # Load environment variables if parameters not provided
    # Look for .env file in both the current directory and parent directory
    if None in (server, database, username, password):
        # Try to load from .env files in different locations
        env_locations = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # Project root .env
            os.path.join(os.path.dirname(__file__), '.env'),  # Current directory .env
            os.path.join(os.path.expanduser('~'), '.env')    # User home directory .env
        ]
        
        env_loaded = False
        for env_path in env_locations:
            if os.path.exists(env_path):
                dotenv.load_dotenv(env_path)
                print(f"Loaded environment variables from {env_path}")
                env_loaded = True
                break
        
        if not env_loaded:
            print("No .env file found. Will use provided parameters or defaults.")
        
        server = server or os.environ.get("server_data_studio") or os.environ.get("SERVER")
        database = database or os.environ.get("database") or os.environ.get("DATABASE")
        username = username or os.environ.get("username") or os.environ.get("USERNAME") or os.environ.get("SQL_USERNAME")
        password = password or os.environ.get("password") or os.environ.get("PASSWORD") or os.environ.get("SQL_PASSWORD")
    
    # Verify required parameters
    if not server:
        print("Error: No server specified. Please provide a server parameter or set it in environment variables.")
        return None, None
    
    if not database:
        print("Error: No database specified. Please provide a database parameter or set it in environment variables.")
        return None, None
      # Ensure auth_type is not None and has a default
    if auth_type is None:
        auth_type = 'windows'  # Default to SQL authentication
    
    # For macOS, SQL auth is the only option, so override auth_type if needed
    if current_platform == 'darwin' and auth_type.lower() != 'sql':
        print(f"Warning: On macOS, only SQL authentication is supported. Changing auth_type from '{auth_type}' to 'sql'.")
        auth_type = 'sql'
        
    if auth_type.lower() == 'sql' and (not username or not password):
        print("Error: SQL authentication requires username and password.")
        return None, None
    
    # Get available ODBC drivers
    available_drivers = get_available_odbc_drivers()
    if not available_drivers:
        print("Error: No suitable ODBC drivers found for SQL Server")
        return None, None
    
    # Define authentication strategies to try (in order of preference)
    auth_strategies = []
    
    # Add preferred authentication first
    if auth_type.lower() == 'windows':
        if current_platform == 'windows':
            auth_strategies.append(('windows', None, None))
        # Add SQL auth as fallback if credentials provided
        if username and password:
            auth_strategies.append(('sql', username, password))
    elif auth_type.lower() == 'sql':
        if username and password:
            auth_strategies.append(('sql', username, password))
        # Add Windows auth as fallback on Windows systems
        if current_platform == 'windows':
            auth_strategies.append(('windows', None, None))
    else:
        print(f"Warning: Invalid authentication type '{auth_type}'. Trying available methods...")
        # Try both if auth_type is invalid
        if username and password:
            auth_strategies.append(('sql', username, password))
        if current_platform == 'windows':
            auth_strategies.append(('windows', None, None))
    
    if not auth_strategies:
        print("Error: No valid authentication methods available. Provide username/password for SQL auth.")
        return None, None
    
    # Track connection attempts and errors
    connection_attempts = []
    
    # Try each authentication strategy with available drivers
    for auth_method, auth_user, auth_pass in auth_strategies:
        for driver in available_drivers:
            try:
                conn_str = build_connection_string(
                    driver, server, database, auth_method, auth_user, auth_pass, current_platform
                )
                
                print(f"Attempting connection: {auth_method} auth using {driver}")
                print(f"Server: {server}, Database: {database}")
                
                conn = pyodbc.connect(conn_str, timeout=10)
                cursor = conn.cursor()
                
                # Test the connection
                cursor.execute("SELECT 1")
                cursor.fetchone()
                
                print(f"✓ Successfully connected to SQL Server")
                print(f"  Server: {server}")
                print(f"  Database: {database}")
                print(f"  Authentication: {auth_method}")
                print(f"  Driver: {driver}")
                print("="*60)
                
                return conn, cursor
                
            except Exception as e:
                error_msg = f"{auth_method} auth using {driver}: {str(e)}"
                connection_attempts.append(error_msg)
                print(f"✗ Failed: {error_msg}")
                continue
    
    # If we reach here, all connection attempts failed
    print("\n" + "="*60)
    print(f"ERROR: All connection attempts failed for server '{server}', database '{database}'")
    print("="*60)
    print("Attempted authentication methods:")
    for i, attempt in enumerate(connection_attempts, 1):
        print(f"{i:2d}. {attempt}")
    
    print("\nTroubleshooting suggestions:")
    print(f"1. Verify SQL Server is running on '{server}'")
    print(f"2. Verify database '{database}' exists and is accessible")
    print("3. Check firewall settings and network connectivity")
    print("4. Verify authentication credentials")
    if current_platform != 'windows':
        print("5. For non-Windows systems, SQL authentication is typically required")
        print("6. Consider adding TrustServerCertificate=Yes and Encrypt=no for local development")
        print("7. For macOS with Docker SQL Server, ensure the format is 'localhost,1433' (with comma)")
    
    return None, None

def get_available_odbc_drivers():
    """Get list of available SQL Server ODBC drivers, prioritized by version."""
    try:
        all_drivers = pyodbc.drivers()
        sql_drivers = [d for d in all_drivers if 'SQL Server' in d]
        
        if not sql_drivers:
            print("Warning: No SQL Server ODBC drivers found. Install ODBC drivers for SQL Server.")
            print("macOS: brew install msodbcsql17 or brew install msodbcsql18")
            print("See: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server")
            return []
            
        # Priority order for drivers
        driver_priority = [
            'ODBC Driver 18 for SQL Server',
            'ODBC Driver 17 for SQL Server',
            'SQL Server Native Client 11.0',
            'SQL Server Native Client 10.0',
            'SQL Server'
        ]
        
        # Sort drivers by priority
        prioritized_drivers = []
        for preferred in driver_priority:
            if preferred in sql_drivers:
                prioritized_drivers.append(preferred)
        
        # Add any remaining drivers
        for driver in sql_drivers:
            if driver not in prioritized_drivers:
                prioritized_drivers.append(driver)
                
        print(f"Available SQL Server drivers: {', '.join(prioritized_drivers)}")
        return prioritized_drivers
    except Exception as e:
        print(f"Error detecting ODBC drivers: {e}")
        return []  # Empty list to indicate failure

def build_connection_string(driver, server, database, auth_type, username=None, password=None, platform='windows'):
    """Build connection string based on authentication type and platform."""
    base_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
    
    if auth_type == 'windows':
        # Windows authentication
        return base_str + "Trusted_Connection=yes;"
    elif auth_type == 'sql':
        # SQL Server authentication
        if not username or not password:
            raise ValueError("Username and password required for SQL authentication")
        
        conn_str = base_str + f"UID={username};PWD={password};"
        
        # Add additional parameters for non-Windows platforms or Docker/containerized SQL Server
        if platform != 'windows':
            conn_str += "TrustServerCertificate=Yes;Encrypt=no;LoginTimeout=30;"
        
        return conn_str
    else:
        raise ValueError(f"Invalid authentication type: {auth_type}")

# Test function
def test_connection():
    """Test function demonstrating usage with your working example."""
    print("Testing SQL Server connection...")
    print(f"Platform: {platform.system()}")
    
    # List of connection configurations to try, in order of priority
    connection_configs = [
        {
            'name': "Environment variables",
            'server': os.environ.get("server_data_studio"),
            'database': os.environ.get("database"),
            'auth_type': 'sql',
            'username': os.environ.get("username"),
            'password': os.environ.get("password")
        },
        {
            'name': "Docker SQL Server (localhost,1433)",
            'server': "localhost,1433",
            'database': "master",
            'auth_type': 'sql',
            'username': "SA",
            'password': os.environ.get("password")
        },
        {
            'name': "Docker SQL Server (127.0.0.1,1433)",
            'server': "127.0.0.1,1433",
            'database': "master",
            'auth_type': 'sql',
            'username': "SA",
            'password': os.environ.get("password")
        },
        {
            'name': "Docker SQL Server (localhost, default port)",
            'server': "localhost",
            'database': "master",
            'auth_type': 'sql',
            'username': "SA",
            'password': os.environ.get("password")
        },
        {
            'name': "Docker SQL Server (127.0.0.1, default port)",
            'server': "127.0.0.1",
            'database': "master",
            'auth_type': 'sql',
            'username': "SA",
            'password': os.environ.get("password")
        }
    ]
    
    conn = None
    cursor = None
    
    # Try each configuration until successful
    for config in connection_configs:
        print(f"\nAttempt: {config['name']}")
        conn, cursor = connect_to_sql_server(
            server=config['server'],
            database=config['database'],
            auth_type=config['auth_type'],
            username=config['username'],
            password=config['password']
        )
        
        if conn:
            print(f"✅ Successfully connected using {config['name']} configuration")
            break
    
    if conn:
        try:
            # Test basic query first
            print("Testing basic query...")
            cursor.execute("SELECT 1 AS test_value")
            row = cursor.fetchone()
            print(f"Basic query result: {row.test_value}")
            
            # Test more complex query if available
            try:
                print("Testing table query...")
                cursor.execute("SELECT TOP 1 * FROM [master].[dbo].[transaction_history]")
                row = cursor.fetchone()
                if row:
                    print("Successfully queried transaction_history table")
                else:
                    print("No data in transaction_history table")
            except Exception as table_error:
                print(f"Table query error (this is normal if the table doesn't exist yet): {table_error}")

        except Exception as e:
            print(f"Error executing test query: {e}")
        finally:
            cursor.close()
            conn.close()
            print("Connection closed successfully")
    else:
        print("Failed to establish connection with any configuration.")
        print("\nPossible Solutions:")
        print("1. Check if SQL Server is running in Docker: 'docker ps'")
        print("2. Restart SQL Server container: 'docker restart sql'")
        print("3. Check container logs: 'docker logs sql'")
        print("4. Verify the password: The default SA password must meet complexity requirements")
        print("5. For macOS, ensure you're using SQL authentication with a properly configured Docker SQL Server")

if __name__ == "__main__":
    test_connection()