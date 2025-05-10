from flask import Flask
from home.routes import home_blueprint
import os

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

app.register_blueprint(home_blueprint)

if __name__ == '__main__':
    app.run(debug=True) 