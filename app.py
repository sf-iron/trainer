from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail

import os

app = Flask(__name__)
# app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
CORS(app)
mail = Mail(app)


from api import *
from models import *

if __name__ == "__main__":
    app.debug = True
    app.run()