from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail

application = Flask(__name__)
# application.config.from_pyfile('config.py')
db = SQLAlchemy(application)
CORS(application)
mail = Mail(application)


if __name__ == "__main__":
    application.debug = True
    application.run()