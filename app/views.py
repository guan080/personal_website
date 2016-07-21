# coding:utf-8
from flask import render_template, url_for, redirect, request, flash, abort
from . import app
from flask_login import login_required, current_user, login_user, logout_user
from .forms import LoginForm, EditorForm
from .models import User, Post, MicroPost, Tag
from app import db
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# 主页路由
@app.route('/')
@app.route('/index')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)


# 登陆界面路由
@app.route('/alibaba', methods=['GET', 'POST'])
def alibaba():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for("index"))
        flash('Wrong email or password, please retry!')
    return render_template('alibaba.html', form=form)


# 注销登陆
@app.route('/logout')
def logout():
    logout_user()
    flash('您已退出登录！')
    return redirect(url_for('index'))


# 后台文章编写界面路由
@app.route('/reedit_post', methods=['GET', 'POST'])
@login_required
def edit_post():
    form = EditorForm()
    if form.validate_on_submit():
        post = Post()
        post.title = form.title.data
        post.content = form.content.data
        # 将tag列表处理成Tag对象
        taglist = form.tag.data.split()
        for tmp in taglist:
            post.tags.append(tmp)
        db.session.add(post)
        flash('文章发表成功！')
        return redirect(url_for('post', posttitle=post.title))
    if current_user is None:
        flash('请先登录！')
        return redirect(url_for('index'))
    return render_template('edit_post.html', form=form)


# 后台文章修改界面路由
@app.route('/reedit_post/<posttitle>', methods=['GET', 'POST'])
@login_required
def reedit_post(posttitle):
    post = Post.query.filter_by(title=posttitle).first()
    if post is None:
        abort(404)
    form = EditorForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        taglist = form.tag.data.split()
        for tmp in taglist:
            post.tags.append(tmp)
        db.session.add(post)
        flash('文章更新成功！')
        return redirect(url_for('post', posttitle=post.title))
    form.title.data = post.title
    form.content.data = post.content
    tags = ''
    for tmp in post.tags:
        tags += tmp.tagname
    form.tag.data = tags
    return render_template('edit_post.html', form=form, post=post)


# 文章内页路由
@app.route('/post/<posttitle>')
def post(posttitle):
    post = Post.query.filter_by(title=posttitle).first()
    post.views += 1
    return render_template('post.html', post=post)


# 按tag筛选后的页面路由
@app.route('/tag/<tagname>')
def tag(tagname):
    tag = Tag()
    tag.tagname = tagname
    posts = tag.posts.all()
    return render_template('tag.html', tagname=tagname, posts=posts)


# 出错处理路由
@app.errorhandler(404)
def page_not_found(e):
    render_template('404.html'), 404
