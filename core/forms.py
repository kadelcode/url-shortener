from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from .models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp, Email, EqualTo
from flask_login import current_user


class LoginForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign in')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(2, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[DataRequired(), 
        EqualTo('password1', message='Passwords must match.'),
        Length(min=8, message='Password must be at least 8 characters long.'),
        ])
    password1 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Sign up')

    # Checks if the email already exist in database
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
    
    # Checks if the username already exist in database
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class EditProfileForm(FlaskForm):
    profile_photo = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        'Usernames must have only letters, numbers, dots or underscores')])
    first_name = StringField('First Name', validators=[Length(0, 64)])
    last_name = StringField('Last Name', validators=[Length(0, 64)])
    submit = SubmitField('Update Profile')

    # Checks if the email already exist in database
    def validate_email(self, field):
        if field.data != current_user.email:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('Email already registered.')
    
    # Checks if the username already exist in database
    def validate_username(self, field):
        if field.data != current_user.username:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError('Username already in use.')