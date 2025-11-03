"""
Test SQL Server Connection with Settings
This script tests if the application can connect to SQL Server using the Settings class.
"""

import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

from app.config.settings import Settings
from app.db.sql_connector import connect_to_sql_server

def test_connection_with_settings():
    """Test SQL Server connection using Settings class."""
    print("="*60)
    print("Testing SQL Server Connection with Settings")
    print("="*60)
    
    # Load settings
    settings = Settings()
    
    print("\n📋 Database Configuration from Settings:")
    print(f"  Server: {settings.db_server}")
    print(f"  Database: {settings.db_database}")
    print(f"  Auth Type: {settings.db_auth_type}")
    print(f"  Username: {settings.db_username if settings.db_username else '(Windows Auth)'}")
    print(f"  Password: {'***' if settings.db_password else '(Windows Auth)'}")
    
    print("\n🔌 Attempting connection...")
    
    # Try to connect using settings
    conn, cursor = connect_to_sql_server(
        server=settings.db_server,
        database=settings.db_database,
        auth_type=settings.db_auth_type,
        username=settings.db_username,
        password=settings.db_password
    )
    
    if conn and cursor:
        print("\n✅ SUCCESS! Connection established.")
        
        try:
            # Test a simple query
            print("\n🧪 Testing basic query...")
            cursor.execute("SELECT @@VERSION AS version")
            row = cursor.fetchone()
            print(f"✅ SQL Server Version: {row.version[:100]}...")
            
            # Test listing tables
            print("\n🧪 Testing table list query...")
            cursor.execute("""
                SELECT TABLE_SCHEMA, TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            tables = cursor.fetchall()
            
            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for i, table in enumerate(tables[:5], 1):  # Show first 5 tables
                    print(f"  {i}. {table.TABLE_SCHEMA}.{table.TABLE_NAME}")
                if len(tables) > 5:
                    print(f"  ... and {len(tables) - 5} more tables")
            else:
                print("⚠️  No tables found in database")
            
        except Exception as e:
            print(f"❌ Error executing test query: {e}")
        finally:
            cursor.close()
            conn.close()
            print("\n🔌 Connection closed.")
    else:
        print("\n❌ FAILED! Could not establish connection.")
        print("\n💡 Troubleshooting:")
        print("  1. Check if SQL Server is running")
        print("  2. Verify server name: localhost\\SQLEXPRESS")
        print("  3. Ensure Windows Authentication is enabled")
        print("  4. Check SQL Server Configuration Manager")
        print("  5. Verify SQL Server Browser service is running")
    
    print("\n" + "="*60)

def test_direct_env_variables():
    """Test connection using environment variables directly."""
    import os
    from dotenv import load_dotenv, find_dotenv
    
    print("\n" + "="*60)
    print("Testing Environment Variables")
    print("="*60)
    
    load_dotenv(find_dotenv())
    
    print("\n📋 Environment Variables:")
    env_vars = [
        'server', 'database', 'auth_type',
        'DB_SERVER', 'DB_DATABASE', 'DB_AUTH_TYPE',
        'server_data_studio', 'SERVER', 'DATABASE'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: (not set)")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("\n🚀 SQL Server Connection Test\n")
    
    # Test 1: Environment variables
    test_direct_env_variables()
    
    # Test 2: Connection with Settings
    test_connection_with_settings()
    
    print("\n✅ Test complete!")
