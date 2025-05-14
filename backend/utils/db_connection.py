import mysql.connector
from mysql.connector import Error
from backend.config import DB_CONFIG

def get_db_connection():
    """
    Creates and returns a database connection
    Returns:
        connection: MySQL database connection object
    """
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def close_db_connection(connection):
    """
    Closes the database connection
    Args:
        connection: MySQL database connection object
    """
    if connection and connection.is_connected():
        connection.close() 