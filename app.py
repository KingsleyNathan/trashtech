from flask import Flask
from backend.routes.dashboard import home_blueprint
from backend.config import configure_email
import os

app = Flask(__name__,
            template_folder='frontend/templates',
            static_folder='frontend/static')

app.register_blueprint(home_blueprint)

# Email Configuration
configure_email(app)

if __name__ == '__main__':
    app.run(debug=True) 