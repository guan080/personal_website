# coding:utf-8
from flask import render_template, url_for, redirect, request, flash
from . import app
from flask_login import login_required, current_user, login_user, logout_user
from .forms import LoginForm
from .models import User


@app.route('/')
@app.route('/index/')
def index():
    return 'Hello world!'


@app.route('/alibaba/', methods=['GET', 'POST'])
@login_required
def alibaba():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            return url_for(index)
        flash('账号或密码错误，请重新登录！')
        return render_template('alibaba.html', form=form)
