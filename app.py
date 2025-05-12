from flask import Flask
from home.routes import home_blueprint
import os

app = Flask(__name__,
            template_folder='frontend/templates',
            static_folder='frontend/static')

app.register_blueprint(home_blueprint)

# Email Configuration for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your Gmail address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Your Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Same as MAIL_USERNAME
app.config['ALERT_RECIPIENTS'] = os.getenv('ALERT_RECIPIENTS', '').split(',')  # Comma-separated list of email addresses

if __name__ == '__main__':
    app.run(debug=True) 