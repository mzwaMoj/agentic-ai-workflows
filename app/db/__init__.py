"""
Database module - centralized access to database connection utilities.
"""

from .sql_connector import connect_to_sql_server

__all__ = [
    'connect_to_sql_server'
]