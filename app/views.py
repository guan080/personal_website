# coding:utf-8
import sys, time
from flask import render_template, url_for, redirect, request, flash, abort, session
from flask_login import login_required, current_user, login_user, logout_user

from app import app, db, wechat
from .forms import LoginForm, EditorForm
from .models import User, Post, MicroPost, Tag, Category
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import TextMessage, ImageMessage, VoiceMessage, VideoMessage, ShortVideoMessage, LocationMessage,\
                                    LinkMessage, EventMessage
from . import func

reload(sys)
sys.setdefaultencoding('utf-8')

recent_posts = Post.query.order_by(Post.timestamp.desc()).limit(5).all()
all_categories = Category.query.all()
all_tags = Tag.query.all()


# 主页路由
@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', posts=posts, Category=Category, recent_posts=recent_posts,
                           all_categories=all_categories, all_tags=all_tags, pagination=pagination)


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
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
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
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
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
    return render_template('post.html', Category=Category, post=post, recent_posts=recent_posts,
                           all_categories=all_categories, all_tags=all_tags)


# 按tag筛选后的页面路由
@app.route('/tag/<name>')
def tag(name):
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.filter_by(name=name).first()
    pagination = tag.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('tag.html', name=name, posts=posts, pagination=pagination, recent_posts=recent_posts,
                           all_categories=all_categories, all_tags=all_tags, Category=Category)


@app.route('/category/<name>')
def category(name):
    page = request.args.get('page', 1, type=int)
    category = Category.query.filter_by(name=name).first()
    pagination = category.posts.paginate(
        page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('category.html', posts=posts, name=name, recent_posts=recent_posts,
                           all_categories=all_categories, all_tags=all_tags, pagination=pagination, Category=Category)


@app.route('/microposts')
def microposts():
    page = request.args.get('page', 1, type=int)
    pagination = MicroPost.query.order_by(MicroPost.timestamp.desc()).paginate(
        page, per_page=app.config['MICROPOSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('microposts.html', posts=posts, pagination=pagination, recent_posts=recent_posts,
                           all_categories=all_categories, all_tags=all_tags, Category=Category)


@app.route('/delete_micropost/<id>')
def delete_micropost(id):
    micropost = MicroPost.query.filter_by(id=id).first()
    db.session.delete(micropost)
    return redirect(url_for('microposts'))


@app.route('/about')
def about():
    return render_template('about.html', recent_posts=recent_posts,
                           all_categories=all_categories, all_tags=all_tags)


# 微信部分
@app.route('/wechat', methods=['GET', 'POST'])
def wechathandle():
    try:
        wechat.parse_data(request.data)
    except ParseError:
        print 'Invalid Body Text.'
    id = wechat.message.id
    target = wechat.message.target
    source = wechat.message.source
    time = wechat.message.time
    type = wechat.message.type
    raw = wechat.message.raw
    # 设置微信号绑定标志位
    bind = False
    u = User.query.filter_by(email=app.config['ADMIN_EMAIL']).first()
    if u.wechat_open_id == source:
        bind = True
    # TextMessage处理
    if isinstance(wechat.message, TextMessage):
        content = wechat.message.content

        # 微信号已绑定
        if bind:
            if content == 'cxbd' or content == 'bdcx' or content == '查询绑定' or content == '绑定查询':
                return wechat.response_text(content='已绑定')
            # 解绑微信号
            if content[:3] == 'jb ' or content[:3] == '解绑 ':
                strs = content.split(' ', 2)
                if len(strs) < 2:
                    return wechat.response_text(content='What are you 弄啥咧？')
                email = strs[1]
                password = strs[2]
                u = User.query.filter_by(email=email).first()
                if u is None:
                    return wechat.response_text(content='What are you 弄啥咧？账号呢？')
                if u.check_password(password):
                    u.wechat_open_id = ''
                    return wechat.response_text(content='账号已解绑')
                else:
                    return wechat.response_text(content='账号不对？密码不对？')
            if content == 'sc' or content == '删除':
                microposts = MicroPost.query.order_by(MicroPost.timestamp.desc()).limit(5).all()
                deleting_microposts = ''
                for micropost in microposts:
                    deleting_microposts = deleting_microposts + 'id: ' + str(micropost.id) + '\n' + \
                                        micropost.content + '\n\n'
                    app.config['MICROPOST_DELETE_ID_LIST'].append(str(micropost.id))
                app.config['MICROPOST_DELETE_FLAG'] = True
                return wechat.response_text(content=deleting_microposts)
            if app.config['MICROPOST_DELETE_FLAG']:
                if content in app.config['MICROPOST_DELETE_ID_LIST']:
                    delete_id = int(content)
                    micropost = MicroPost.query.filter_by(id=delete_id).first()
                    db.session.delete(micropost)
                    app.config['MICROPOST_DELETE_FLAG'] = False
                    return wechat.response_text(content=content + '号说说已删除')
                app.config['MICROPOST_DELETE_FLAG'] = False
                return wechat.response_text(content='请重新提交删除指令')
            if content[:3] == 'ss ' or content[:3] == '说说 ':
                strs = content.split(' ', 1)
                if len(strs) < 2:
                    return wechat.response_text(content='弄啥咧？内容呢？')
                content = strs[1]
                micropost = MicroPost()
                micropost.content = content
                db.session.add(micropost)
                return wechat.response_text(content='说说已发表')
            # content = func.wiki(content)
            return wechat.response_text(content=content)
        # 微信号未绑定
        else:
            if content == 'cxbd' or content == 'bdcx' or content == '查询绑定' or content == '绑定查询':
                return wechat.response_text(content='未绑定')
            # 绑定微信号
            if content[:3] == 'bd ' or content[:3] == '绑定 ':
                strs = content.split(' ', 2)
                if len(strs) < 2:
                    return wechat.response_text(content='What are you 弄啥咧？')
                email = strs[1]
                password = strs[2]
                u = User.query.filter_by(email=email).first()
                if u is None:
                    return wechat.response_text(content='What are you 弄啥咧？账号呢？')
                if u.wechat_open_id == source:
                    return wechat.response_text(content='账号已经绑定过')
                if u.check_password(password):
                    u.wechat_open_id = source
                    return wechat.response_text(content='账号绑定成功')
                else:
                    return wechat.response_text(content='账号不对？密码不对？')
            # content = func.wiki(content)
            return wechat.response_text(content=content)
    if isinstance(wechat.message, ImageMessage):
        picurl = wechat.message.picurl
        media_id = wechat.message.media_id
        return wechat.response_image(media_id=media_id)
    if isinstance(wechat.message, VoiceMessage):
        media_id = wechat.message.media_id
        format = wechat.message.format
        recognition = wechat.message.recognition
        return wechat.response_voice(media_id=media_id)
    if isinstance(wechat.message, VideoMessage) or isinstance(wechat.message, ShortVideoMessage):
        media_id = wechat.message.media_id
        thumb_media_id = wechat.message.thumb_media_id
        return wechat.response_video(media_id=media_id)
    if isinstance(wechat.message, LocationMessage):
        location = wechat.message.location
        scale = wechat.message.scale
        label = wechat.message.label
        return wechat.response_none()
    if isinstance(wechat.message, EventMessage):
        if wechat.message.type == 'subscribe':  # 关注事件(包括普通关注事件和扫描二维码造成的关注事件)
            key = wechat.message.key  # 对应于 XML 中的 EventKey (普通关注事件时此值为 None)
            ticket = wechat.message.ticket  # 对应于 XML 中的 Ticket (普通关注事件时此值为 None)
        elif wechat.message.type == 'unsubscribe':  # 取消关注事件（无可用私有信息）
            pass
        elif wechat.message.type == 'scan':  # 用户已关注时的二维码扫描事件
            key = wechat.message.key  # 对应于 XML 中的 EventKey
            ticket = wechat.message.ticket  # 对应于 XML 中的 Ticket
        elif wechat.message.type == 'location':  # 上报地理位置事件
            latitude = wechat.message.latitude  # 对应于 XML 中的 Latitude
            longitude = wechat.message.longitude  # 对应于 XML 中的 Longitude
            precision = wechat.message.precision  # 对应于 XML 中的 Precision
        elif wechat.message.type == 'click':  # 自定义菜单点击事件
            key = wechat.message.key  # 对应于 XML 中的 EventKey
        elif wechat.message.type == 'view':  # 自定义菜单跳转链接事件
            key = wechat.message.key  # 对应于 XML 中的 EventKey
        elif wechat.message.type == 'templatesendjobfinish':  # 模板消息事件
            status = wechat.message.status  # 对应于 XML 中的 Status
        elif wechat.message.type in ['scancode_push', 'scancode_waitmsg', 'pic_sysphoto',
                                     'pic_photo_or_album', 'pic_weixin', 'location_select']:  # 其他事件
            key = wechat.message.key  # 对应于 XML 中的 EventKey
        return wechat.response_none()


# @app.route('/wexin')
# def wexin():
#     raw = app.config['RAW']
#     return render_template('wexin.html', raw=raw)


# 404处理路由
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

