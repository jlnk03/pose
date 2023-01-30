from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from functools import wraps


db = SQLAlchemy()


def active_required(func):

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.active:
            return redirect('/verify_mail')
            # return redirect(url_for('auth.verify'))
        return func(*args, **kwargs)

    return decorated_view


def protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(active_required(dashapp.server.view_functions[view_func]))
    return dashapp


def create_app():
    app = Flask(__name__, static_folder='assets')
    app.title = 'SwingAnalysis'

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../db.sqlite'

    db.init_app(app)

    from models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # from flask_wrapper.app_flask import init_dash
    from app_flask import init_dash
    app = init_dash(app)

    app = protect_dashviews(app)

    return app.server