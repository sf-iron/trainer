import random
import string
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func, String, Boolean

from email_validator import validate_email, EmailNotValidError

from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired)

db_endpoint = os.environ['DB_ENDPOINT']
engine = create_engine(db_endpoint, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

auth_secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
activate_secret_key = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(32))


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(Text, unique=True, index=True)
    password_hash = Column(Text)
    activated = Column(Boolean, default=False)
    activated_at = Column(DateTime)

    def __init__(self, email, password):
        try:
            v = validate_email(email)  # validate and get info
            self.email = v["email"]  # replace with normalized form
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            raise e

        self.password_hash = pwd_context.encrypt(password)

    def generate_activation_key(self):
        s2 = Serializer(activate_secret_key)
        activation_key = s2.dumps({'id': self.id})
        # print(activation_key + "generate")
        return activation_key

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self):
        s1 = Serializer(auth_secret_key)
        return s1.dumps({'id': self.id})

    @staticmethod
    def verify_activation_key(activation_key):
        s2 = Serializer(activate_secret_key)
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
