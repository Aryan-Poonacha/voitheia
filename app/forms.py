from flask_wtf import FlaskForm

from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, BooleanField, PasswordField, TextAreaField #normal form validators
from wtforms.fields.html5 import EmailField #html5 form validators

from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('username', validators = [DataRequired(), Length(min = 3, max = 120)])
    password=PasswordField('password', validators = [DataRequired(), Length(min = 8, max = 120)])
    remember_me = BooleanField('remember_me', default = False)

class CauseForm(FlaskForm):
    name = StringField('name', validators = [DataRequired(), Length(min = 2, max = 120)])

class RegisterForm(FlaskForm):
    username = StringField('username', validators = [DataRequired(), Length(min = 2, max = 120)])
    password=PasswordField('password', validators = [DataRequired(),Length(min=2), EqualTo('confirm_password'), Length(min = 8, max = 120)])
    confirm_password = PasswordField('confirm_password', validators = [DataRequired(), Length(min = 8, max = 120)])
    remember_me = BooleanField('remember_me', default = False)
    email = EmailField('email', validators = [DataRequired(), Email()])
    newsletter_subscribe = BooleanField('newsletter_subscribe', default = False)
    recaptcha = RecaptchaField()

class ForgotPasswordForm1(FlaskForm):
    email = StringField('email', validators = [DataRequired(), Length(max = 120)])

class ForgotPasswordForm2(FlaskForm):
    password=PasswordField('password', validators = [DataRequired(),Length(min=2), EqualTo('confirm_password'), Length(min = 8, max = 120)])
    confirm_password = PasswordField('confirm_password', validators = [DataRequired(), Length(min = 8, max = 120)])

class NewsletterForm(FlaskForm):
    email = EmailField('email', validators = [DataRequired(), Email(), Length(max = 120)])

class CauseSubmissionForm(FlaskForm):
    cause_name = StringField('name', validators = [DataRequired(), Length(min = 2, max = 120)])
    email = EmailField('email', validators = [DataRequired(), Email(), Length(max = 120)])
    description = TextAreaField('name', validators = [DataRequired(), Length(max = 2000)])
    recaptcha = RecaptchaField()
