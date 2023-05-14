from datetime import datetime

from flask_wrapper import db
from .models import User


# set signup_date to current time if not set
def set_signup_date():
    users = User.query.all()

    for user in users:
        if user.signup_date is None:
            user.signup_date = datetime.now()

    db.session.commit()
