from flask import request, jsonify, g, abort
from flask_httpauth import HTTPBasicAuth
from datetime import datetime
import datetime
from flask_mail import Message

from application import  db, mail
from models import User

auth = HTTPBasicAuth()


def send_msg(subject, body, recipients=["josh@sf-iron.com"]):
    try:
        msg = Message(
            sender=app.config['MAIL_USERNAME'],
            subject=subject,
            body=body,
            recipients=recipients)
        mail.send(msg)
    except Exception as e:
        print(e)


def generate_activation_url(user):
    activation_key = user.generate_activation_key()
    return "http://localhost:8080/#/activate/" + activation_key


@auth.verify_password
def verify_password(email_or_token, password):
    user_id = User.verify_auth_token(email_or_token)
    print(user_id)
    if user_id:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    else:
        user = User.query.filter_by(email=email_or_token).first()
        print(user)
        if (not user) and (not user.verify_password(password)):
            return False
    if not user.account_activated:
        return False
    g.user = user
    print(g.user)
    return True


@app.route("/")
def home():
    return jsonify({'message': 'Welcome'})


@app.route("/users", methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')

        if not email or not password:
            abort(400)

        try:
            user = User(email=email, password=password)
            # user.hash_password(password)
            db.session.add(user)
            db.session.commit()
            activation_url = generate_activation_url(user)

            send_msg('Activate your account', 'Activation URL: ' + activation_url)
            goal = Goals(user_id=user.id)
            db.session.add(goal)
            db.session.commit()
            return jsonify({'email': user.email, 'user_id': user.id, 'activation_url': activation_url}), 201
        except Exception as e:
            print(e)
            abort(422)


@app.route("/user-activation/<activation_key>")
def activate_user(activation_key):
    user_id = User.verify_activation_key(activation_key)
    # print(user_id)
    if user_id:
        user = User.query.filter_by(id=user_id).first()
        user.account_activated = True
        user.activated_at = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        print(user)
        return jsonify({'user_id': user.id})
    else:
        abort(400)


@app.route('/user-activation', methods=['POST'])
def resend_email():
    email = request.json.get('email')
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            send_msg('Activate your account', 'Activation URL: ' + generate_activation_url(user))
            return jsonify({'user_id': user.id})
    except Exception as e:
        print(e)
        abort(401)


@app.route("/token")
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token})


@app.route("/user")
@auth.login_required
def user():
    return jsonify({'email': g.user.email, 'user_id': g.user.id}), 200