from .import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class TwitterData(db.Model):
    id = db.Column(db.Integer, primary_key=True) #primary key
    user_access_token = db.Column(db.String(150))
    user_access_token_secret = db.Column(db.String(150))
    last_fetch = db.Column(db.DateTime(timezone=True))
    last_fetch_pos = db.Column(db.Integer)
    last_fetch_negative = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id")) #foreign key

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) #primary key
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    location = db.Column(db.String(150))
    twitter_data = db.relationship("TwitterData")