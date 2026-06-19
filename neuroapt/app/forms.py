from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from neuroapt.app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    user_type = RadioField('Login As', choices=[('user', 'User'), ('admin', 'Administrator')], default='user')
    submit = SubmitField('Login')

class QuestionForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    content = TextAreaField('Question Content', validators=[DataRequired()])
    submit = SubmitField('Add Question')

class OptionForm(FlaskForm):
    content = TextAreaField('Option Content', validators=[DataRequired()])
    is_correct = BooleanField('Correct Answer')
    score_value = StringField('Score Value', validators=[DataRequired()])
    submit = SubmitField('Add Option')

class TestAnswerForm(FlaskForm):
    answer = RadioField('Answer', coerce=int)
    submit = SubmitField('Next') 