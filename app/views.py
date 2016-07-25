# coding:utf-8
from flask import render_template, url_for, redirect, request, flash, abort
from . import app
from flask_login import login_required, current_user, login_user, logout_user
from .forms import LoginForm, EditorForm
from .models import User, Post, MicroPost, Tag, Category
from app import db
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# 主页路由
@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', posts=posts, Category=Category, pagination=pagination)


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
@app.route('/edit_post', methods=['GET', 'POST'])
@login_required
def edit_post():
    form = EditorForm()
    if form.validate_on_submit():
        post = Post()
        post.title = form.title.data
        post.category_id = form.category.data
        post.content = form.content.data
        # 将tag列表处理成Tag对象
        taglist = form.tag.data.split()
        for tmp in taglist:
            if Tag.query.filter_by(name=tmp).first() is None:
                newtag = Tag()
                newtag.name = tmp
                db.session.add(newtag)
            tag = Tag.query.filter_by(name=tmp).first()
            post.tags.append(tag)
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
        for tmp in post.tags.all():
            post.tags.remove(tmp)
        post.title = form.title.data
        post.category_id = form.category.data
        post.content = form.content.data
        tag_list = form.tag.data.split()
        for tmp in tag_list:
            if Tag.query.filter_by(name=tmp).first() is None:
                newtag = Tag()
                newtag.name = tmp
                db.session.add(newtag)
            tag = Tag.query.filter_by(name=tmp).first()
            post.tags.append(tag)
        db.session.add(post)
        flash('文章更新成功！')
        return redirect(url_for('post', posttitle=post.title))
    form.title.data = post.title
    form.content.data = post.content
    tags = ''
    for tmp in post.tags:
        tags += tmp.name + " "
    form.tag.data = tags
    return render_template('edit_post.html', form=form, post=post)


# 文章内页路由
@app.route('/post/<posttitle>')
def post(posttitle):
    post = Post.query.filter_by(title=posttitle).first()
    post.views += 1
    return render_template('post.html', post=post)


# 按tag筛选后的页面路由
@app.route('/tag/<name>')
def tag(name):
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.filter_by(name=name).first()
    pagination = tag.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('tag.html', name=name, posts=posts, pagination=pagination, Category=Category)


@app.route('/category/<name>')
def category(name):
    page = request.args.get('page', 1, type=int)
    category = Category.query.filter_by(name=name).first()
    pagination = category.posts.paginate(
        page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('category.html', posts=posts, name=name, Category=Category, pagination=pagination)


@app.route('/microposts')
def microposts():
    page = request.args.get('page', 1, type=int)
    pagination = MicroPost.query.order_by(MicroPost.timestamp.desc()).paginate(
        page, per_page=app.config['MICROPOSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('microposts.html', posts=posts, pagination=pagination)


@app.route('/about')
def about():
    return render_template('about.html')


# 404处理路由
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

