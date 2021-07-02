from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from geektext.models import User


class RegistrationForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(max=30)])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    home_address = StringField('Home Address', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class EditUserProfileForm(FlaskForm):
   #shipping_address = StringField('Shipping Address', validators=[DataRequired(), Length(max=100)])
    name = StringField('Name',
                       validators=[ Length(max=30)])
    username = StringField('Username',
                           validators=[Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    home_address = StringField('Home Address', validators=[Length(max=100)])
    submit = SubmitField('Submit')

class BillingForm(FlaskForm):
    card_type = SelectField('Card Type', choices=['Visa', 'MasterCard', 'Discover', 'American Express'])
    card_number = StringField('Card Number', validators=[Length(min=16, max=20)])
    cvv = IntegerField('CVV')
    exp_date = DateField('Expiration Date')
    submit = SubmitField('Submit')
