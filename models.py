from app import db
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired)
import random, string
from email_validator import validate_email, EmailNotValidError

auth_secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
activate_secret_key = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(32))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, index=True)
    password_hash = db.Column(db.String(256))
    phone_number = db.Column(db.String(20), unique=True)
    account_activated = db.Column(db.Boolean, default=False)
    activated_at = db.Column(db.DateTime)

    def __init__(self, email, password):
        try:
            v = validate_email(email)  # validate and get info
            self.email = v["email"]  # replace with normalized form
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            raise (e)

        self.password_hash = self.hash_password(password)

    def hash_password(self, password):
        return pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self):
        s1 = Serializer(auth_secret_key)
        return s1.dumps({'id': self.id})

    def generate_activation_key(self):
        s2 = Serializer(activate_secret_key)
        activation_key = s2.dumps({'id': self.id})
        # print(activation_key + "generate")
        return activation_key

    @staticmethod
    def verify_activation_key(activation_key):
        s2 = Serializer(activate_secret_key)
        # print(s.loads(activation_key))
        # print(s2.loads(activation_key))
        try:
            print(activation_key + " verify")
            data = s2.loads(activation_key, max_age=86400)

        except SignatureExpired as e:
            print("SignatureExpired")
            print(e)
            # Valid Token, but expired
            return None
        except BadSignature as e:
            print("BadSignature")
            print(e)
            # Invalid Token
            return None
        user_id = data['id']
        return user_id

    @staticmethod
    def verify_auth_token(token):
        s1 = Serializer(auth_secret_key)
        try:
            data = s1.loads(token, max_age=86400)
        except SignatureExpired as e:
            print(e)
            # Valid Token, but expired
            return None
        except BadSignature as e:
            print(e)
            # Invalid Token
            return None
        user_id = data['id']
        return user_id