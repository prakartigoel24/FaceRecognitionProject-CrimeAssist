from flask_sqlalchemy import SQLAlchemy          # Handles Database
from flask import Flask, url_for                 # To handle URLs
from flask_bcrypt import Bcrypt                  # To hash User Passwords
from flask_table import*                         # Flask tables to store data
from flask_login import LoginManager             # To handle User Login sessions
from flask_mail import Mail                      # To handle mails (for reset password)
import os

app = Flask(__name__, static_folder='static')

# General and DB configs
app.config['SECRET_KEY'] = 'e1eade5b86a048a0fc060b0dfc51990a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join(app.root_path,'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.app_context().push()

# Login related configurations
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Mail related configurations
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'youremail@gmail.com'   # Testing Email
app.config['MAIL_PASSWORD'] = 'yourpassword'         # Testing Email Password
mail = Mail(app)


from crimeassist import routes
