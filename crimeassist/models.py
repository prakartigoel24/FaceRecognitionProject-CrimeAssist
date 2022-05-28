from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from email.policy import default
from flask_login import UserMixin
from crimeassist import db, login_manager, app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    image_file = db.Column(db.String(20),default = None)
    password = db.Column(db.String(60),nullable = False)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"


class Convict(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(25),nullable=False)
    dob = db.Column(db.Date ,nullable = False)
    profile_image = db.Column(db.String(20),nullable=False)
    crimes = db.Column(db.Text,nullable=False)

    def __repr__(self):
        return f"Convict('{self.name}', '{self.crimes}','{self.dob}', '{self.profile_image}')"
