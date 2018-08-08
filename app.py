from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS
from flask_mail import Mail

from database import db_session
from schema import schema


application = Flask(__name__, static_folder='static/build')
# application.config.from_pyfile('config.py')
# db = SQLAlchemy(application)
CORS(application)
mail = Mail(application)

application.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True, context={'session': db_session}))


if __name__ == "__main__":
    application.debug = True
    application.run()