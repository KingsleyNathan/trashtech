from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file if present

class Config:
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '')
    MYSQL_USER = os.environ.get('MYSQL_USER', '')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', '')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))