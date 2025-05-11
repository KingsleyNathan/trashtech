import mysql.connector
from mysql.connector import Error
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.config import Config

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def get_test_db_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.TEST_MYSQL_HOST,
            user=Config.TEST_MYSQL_USER,
            password=Config.TEST_MYSQL_PASSWORD,
            database=Config.TEST_MYSQL_DB,
            port=Config.TEST_MYSQL_PORT
        )
        if connection.is_connected():
            print("Successfully connected to Test MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to Test MySQL database: {e}")
        return None 