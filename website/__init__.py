from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db2 =SQLAlchemy()


DB_NAME2 = 'new_database.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']='secret_key_2001'
    app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{DB_NAME2}'
    
    
    db2.init_app(app)
    from .views import views
    from .auth import auth

    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(auth,url_prefix ='/')

    from website.models2 import Business

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view= 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Business.query.get(int(id))

    return app

def create_database(app):
    with app.app_context():
        db2.create_all()



    