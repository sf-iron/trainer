from flask import Flask
from flask_cors import CORS
from flask_mail import Mail

application = Flask(__name__, static_folder='static/build/static')
application.config.from_pyfile('config.py')
CORS(application)
mail = Mail(application)

from api import *

if __name__ == "__main__":
    application.debug = True
    application.run()
