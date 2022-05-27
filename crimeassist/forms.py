from collections import UserString
from logging import PlaceHolder
from wsgiref.validate import validator
from xml.dom import ValidationErr

from flask import Flask
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import*
from wtforms.validators import*
from crimeassist.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired() , Length(min=2, max=20) ])

    email = StringField('Email',
                            validators=[DataRequired(),Email()])

    password = PasswordField('Password',
                            validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')])
                        
    submit  = SubmitField('Sign Up')

    def validate_username(self,username):
        user  = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken , please choose a different one.')


    def validate_email(self,email):
        user  = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken , please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                            validators=[DataRequired(),Email()])

    password = PasswordField('Password',
                            validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit  = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired() , Length(min=2, max=20) ])

    email = StringField('Email',
                            validators=[DataRequired(),Email()])
   
    password = PasswordField('Previous Password')

    confirm_password = PasswordField('New Password')
                        
    
    submit  = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user  = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken , please choose a different one.')


    def validate_email(self,email):
        if email.data != current_user.email:
            user  = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken , please choose a different one.')


class AddConvictForm(FlaskForm):
    name = StringField('Convict Full Name',
                            validators=[DataRequired() , Length(min=2, max=20) ])

    dob = DateField('Date of Birth',validators=[DataRequired()])
    
    picture  = FileField('Convict Face Image', validators =[FileAllowed(['jpg'])])
     
    crimes = TextAreaField('Crimes Committed',validators=[DataRequired()] )                    
    submit  = SubmitField('Add Convict')

class UpdateConvictForm(FlaskForm):
    name = StringField('Convict Full Name',
                            validators=[DataRequired() , Length(min=2, max=25) ])

    dob = DateField('Date of Birth',validators=[DataRequired()])
    
    profile_image  = FileField('Convict Face Image', validators =[FileAllowed(['jpg','png'])])
     
    crimes = TextAreaField('Crimes Committed',validators=[DataRequired()] )                    
    submit  = SubmitField('Update Info')

class SearchForm(FlaskForm):
    search_using = SelectField('Search Using : ', choices = [('name', 'Name'),('id', 'ID'),('dob','D.O.B (yyyy-mm-dd)'),('crimes','Crime')],validate_choice=False)
    search = StringField('Search')
    submit  = SubmitField('Search')

class FaceLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    submit  = SubmitField('Submit')

class ConvictSearchForm(FlaskForm):    
    picture  = FileField('Upload Image', validators =[FileAllowed(['jpg'])])
    submit  = SubmitField('Search')
