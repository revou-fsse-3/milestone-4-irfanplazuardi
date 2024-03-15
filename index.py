from dotenv import load_dotenv
from flask import Flask
from connectors.mysql_connector import engine, connection
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from models.user import User

from flask_login import LoginManager, login_required
import os

from sqlalchemy import select

# Load Controller Files
from controllers.user import user_routes
from controllers.account import account_routes
from controllers.transaction import transaction_routes

load_dotenv()

app=Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.register_blueprint(user_routes)
app.register_blueprint(account_routes)
app.register_blueprint(transaction_routes)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    return session.query(User).get(int(user_id))
# Product Route
@app.route("/")
def hello_world():

    return "<p>Insert Success</p>"