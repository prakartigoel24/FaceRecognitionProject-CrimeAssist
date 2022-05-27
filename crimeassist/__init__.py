from flask_sqlalchemy import SQLAlchemy
from flask import Flask, url_for
from flask_bcrypt import Bcrypt
from flask_table import*
from flask_login import LoginManager

app=Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'e1eade5b86a048a0fc060b0dfc51990a'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
UPLOAD_FOLDER = 'crimeassist/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 24 * 1024 * 1024
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from crimeassist import routes