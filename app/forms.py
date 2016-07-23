# coding:utf-8
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email
from .models import Category


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class EditorForm(Form):
    category = SelectField('分类', validators=[DataRequired()], choices=[])
    title = StringField('标题', validators=[DataRequired()])
    tag = StringField('标签（以空格分隔）')
    content = TextAreaField('正文')
    submit = SubmitField("发布")
