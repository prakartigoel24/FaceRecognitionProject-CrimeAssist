from asyncio.windows_events import NULL
from datetime import datetime
from email.policy import default

from flask_login import UserMixin

from crimeassist import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    image_file = db.Column(db.String(20),nullable=False, default = 'default.jpg')
    password = db.Column(db.String(60),nullable = False)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"


class Convict(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(25),nullable=False)
    dob = db.Column(db.Date ,nullable = False)
    profile_image = db.Column(db.String(20),nullable=False)
    crimes = db.Column(db.Text,nullable=False)
    images = db.relationship('ConvictImage', backref = 'person', lazy=True)

    def __repr__(self):
        return f"Convict('{self.name}', '{self.crimes}','{self.dob}', '{self.profile_image}')"


class ConvictImage(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    person_id = db.Column(db.Integer,db.ForeignKey('convict.id'),nullable=False)
    image_file = db.Column(db.String(20),nullable=False)

    def __repr__(self):
        return f"ConvictImage('{self.person_id}','{self.image_file}')"