import pandas as pd
import numpy as np
import os
import sys
import json
import pyodbc
import random
from faker import Faker
from datetime import datetime, timedelta
import re
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Import the improved SQL connector
from sql_connector import connect_to_sql_server
password = os.environ.get("password")
# =============================================================================
# CONFIGURATION SECTION - Update these settings as needed
# =============================================================================
CONFIG = {
    # Database connection settings
    'server': 'localhost,1433',  # Default server
    'database': 'master',        # Default database
    'auth_type': 'sql',          # 'windows' or 'sql'
    'username': 'SA',            # SQL Server username (required for SQL auth)
    'password': password,  # SQL Server password (required for SQL auth)
    
    # Alternative configurations for different environments
    'environments': {
        'local_docker': {
            'server': 'localhost,1433',
            'database': 'master',
            'auth_type': 'sql',
            'username': 'SA',
            'password': password
        },
        'local_windows': {
            'server': 'localhost\\SQLEXPRESS',
            'database': 'master',
            'auth_type': 'windows',
            'username': None,
            'password': None
        },
        'from_env': {
            'server': os.environ.get("server_data_studio", "localhost,1433"),
            'database': os.environ.get("database", "master"),
            'auth_type': os.environ.get("auth_type", "sql"),
            'username': os.environ.get("username", "SA"),
            'password': password
        }
    }
}
# =============================================================================

def get_connection_config(environment='default'):
    """
    Get connection configuration based on environment.
    
    Args:
        environment (str): Environment name ('default', 'local_docker', 'local_windows', 'from_env')
    
    Returns:
        dict: Connection configuration
    """
    if environment == 'default':
        return {
            'server': CONFIG['server'],
            'database': CONFIG['database'],
            'auth_type': CONFIG['auth_type'],
            'username': CONFIG['username'],
            'password': CONFIG['password']
        }
    elif environment in CONFIG['environments']:
        return CONFIG['environments'][environment]
    else:
        print(f"Warning: Unknown environment '{environment}', using default configuration")
        return get_connection_config('default')