from flask_login import UserMixin
# from flask_wrapper import db
from flask_wrapper import db


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    session_id = db.Column(db.String(100), unique=True)
    time = db.Column(db.DateTime)
    amount = db.Column(db.Integer)
    booked = db.Column(db.Boolean, default=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    active = db.Column(db.Boolean)
    email_new = db.Column(db.String(1000))
    n_analyses = db.Column(db.Integer)
    unlimited = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    subscription = db.Column(db.String(100))
    canceled = db.Column(db.Boolean)
    analyzed = db.Column(db.Integer)



