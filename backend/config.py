from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file if present

class Config:
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '')
    MYSQL_USER = os.environ.get('MYSQL_USER', '')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', '')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

# Database configuration dictionary
DB_CONFIG = {
    'host': Config.MYSQL_HOST,
    'user': Config.MYSQL_USER,
    'password': Config.MYSQL_PASSWORD,
    'database': Config.MYSQL_DB,
    'port': Config.MYSQL_PORT
}

def configure_email(app):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your Gmail address
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Your Gmail App Password
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Same as MAIL_USERNAME
    app.config['ALERT_RECIPIENTS'] = os.getenv('ALERT_RECIPIENTS', '').split(',')  # Comma-separated list of email addresses