# coding:utf-8
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')