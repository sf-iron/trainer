from flask import request, jsonify, g, abort, send_from_directory
from flask_httpauth import HTTPBasicAuth
from flask_graphql import GraphQLView
from datetime import datetime
import datetime
from flask_mail import Message
from app import application, mail
from database import db_session as db, User
from schema import schema

auth = HTTPBasicAuth()


def send_msg(subject, body, html, recipients=["mikeabell2@gmail.com", "josh@sf-iron.com"]):
    try:
        msg = Message(
            sender='trainer@trainer-app.com',
            subject=subject,
            body=body,
            html=html,
            recipients=recipients)
        mail.send(msg)
    except Exception as e:
        print(e)


def generate_activation_url(user):
    activation_key = user.generate_activation_key()
    return "https://www.surewhynotokay.com/activate/" + activation_key


@auth.verify_password
def verify_password(email_or_token, password):
    try:
        print(email_or_token)
        user_id = User.verify_auth_token(email_or_token)
        print(user_id)
        if user_id:
            user = db.query(User).filter_by(id=user_id).first()
            print(user)
        else:
            user = db.query(User).filter_by(email=email_or_token).first()
            print(user)
            if (not user) and (not user.verify_password(password)):
                return False
        if not user.activated:
            return False
        g.user = user
        print(g.user)
        return True
    except Exception as e:
        print(e)
        return False


@application.route('/')
def serve():
   return send_from_directory('static/build', 'index.html')


@application.route("/sign-up", methods=['POST'])
def sign_up():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        abort(400)
    try:
        user = User(email=email, password=password)
        db.add(user)
        db.commit()
        activation_url = generate_activation_url(user)
        send_msg('Activate your account',
                 'Activation URL: ' + activation_url,
                 '<a href="'+activation_url+'" target="_blank">Activate your account</a>')
        return jsonify({'email': user.email, 'user_id': user.id, 'activation_url': activation_url}), 201
    except Exception as e:
        print(e)
        abort(422)


@application.route("/activate/<activation_key>")
def activate_user(activation_key):
    user_id = User.verify_activation_key(activation_key)
    if user_id:
        user = db.query(User).filter_by(id=user_id).first()
        user.activated = True
        user.activated_at = datetime.datetime.now()
        db.add(user)
        db.commit()

        return jsonify({'user_id': user.id})
    else:
        abort(400)


@application.route('/activate', methods=['POST'])
def resend_email():
    email = request.json.get('email')
    try:
        user = db.query(User).filter_by(email=email).first()
        if user:
            send_msg('Activate your account', 'Activation URL: ' + generate_activation_url(user))
            return jsonify({'user_id': user.id})
    except Exception as e:
        print(e)
        abort(401)


@application.route("/token")
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token})


@application.route("/apple-app-site-association")
def universal_links():
    return jsonify({'applinks': {'apps': [], 'details': [{'appID': '29DWXCY7LN.com.sf.iron.trainer', 'paths': ['*']}]}})



@application.route("/graphql", methods=['POST'])
@auth.login_required
def graphql():
    query = request.json.get('query')
    return jsonify({'data': schema.execute(query, context_value={'user': g.user,'session': db}).data})


