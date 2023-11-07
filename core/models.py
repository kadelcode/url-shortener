import os
from core.app import app
from core.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from core.auth import login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_pic = db.Column(db.String(64), default='logo.png')
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    password = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    customshorturls = db.relationship('CustomShortUrls', backref='user')
    # custom_short_urls = db.relationship("CustomShortUrl", backref="user")
 
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
 
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)

        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    def get_username(self):
        return self.username

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])

        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

class ShortUrls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_id = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(), default=datetime.now(), nullable=False)

class CustomShortUrls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    domain = db.Column(db.String(30), nullable=True)
    back_half = db.Column(db.String(100), nullable=True)
    short_id = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(), default=datetime.now(), nullable=False)
    short_url = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))