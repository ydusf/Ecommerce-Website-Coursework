from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_session import Session


db = SQLAlchemy()
DATABASE_NAME = 'database.sqlite3'
lm = LoginManager()
LOGINMANAGER_NAME = 'login'
sess = Session()
SESSION_TYPE = 'filesystem'
bootstrap = Bootstrap5()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ecommerce'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = SESSION_TYPE

    sess.init_app(app)
    db.init_app(app)
    lm.init_app(app)
    lm.login_view = LOGINMANAGER_NAME
    bootstrap.init_app(app)

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')

    create_database(app)

    return app

def create_database(app):
    if not path.exists(f'website/instance/{DATABASE_NAME}'):
        with app.app_context():
            db.create_all()
