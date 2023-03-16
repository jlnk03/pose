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
    last_analyzed = db.Column(db.DateTime)

    # Pelvis Rotation
    setup_low_pelvis_rot = db.Column(db.Integer)
    setup_high_pelvis_rot = db.Column(db.Integer)
    top_low_pelvis_rot = db.Column(db.Integer)
    top_high_pelvis_rot = db.Column(db.Integer)
    impact_low_pelvis_rot = db.Column(db.Integer)
    impact_high_pelvis_rot = db.Column(db.Integer)

    # Pelvis Tilt
    setup_low_pelvis_tilt = db.Column(db.Integer)
    setup_high_pelvis_tilt = db.Column(db.Integer)
    top_low_pelvis_tilt = db.Column(db.Integer)
    top_high_pelvis_tilt = db.Column(db.Integer)
    impact_low_pelvis_tilt = db.Column(db.Integer)
    impact_high_pelvis_tilt = db.Column(db.Integer)

    # Thorax Rotation
    setup_low_thorax_rot = db.Column(db.Integer)
    setup_high_thorax_rot = db.Column(db.Integer)
    top_low_thorax_rot = db.Column(db.Integer)
    top_high_thorax_rot = db.Column(db.Integer)
    impact_low_thorax_rot = db.Column(db.Integer)
    impact_high_thorax_rot = db.Column(db.Integer)

    # Thorax Tilt
    setup_low_thorax_tilt = db.Column(db.Integer)
    setup_high_thorax_tilt = db.Column(db.Integer)
    top_low_thorax_tilt = db.Column(db.Integer)
    top_high_thorax_tilt = db.Column(db.Integer)
    impact_low_thorax_tilt = db.Column(db.Integer)
    impact_high_thorax_tilt = db.Column(db.Integer)

    # Head Rotation
    setup_low_head_rot = db.Column(db.Integer)
    setup_high_head_rot = db.Column(db.Integer)
    top_low_head_rot = db.Column(db.Integer)
    top_high_head_rot = db.Column(db.Integer)
    impact_low_head_rot = db.Column(db.Integer)
    impact_high_head_rot = db.Column(db.Integer)

    # Head Tilt
    setup_low_head_tilt = db.Column(db.Integer)
    setup_high_head_tilt = db.Column(db.Integer)
    top_low_head_tilt = db.Column(db.Integer)
    top_high_head_tilt = db.Column(db.Integer)
    impact_low_head_tilt = db.Column(db.Integer)
    impact_high_head_tilt = db.Column(db.Integer)
