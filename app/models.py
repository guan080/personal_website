# coding: utf-8

from . import db, loginmanager
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        print '<User %r>' % self.email


# 回调函数，用于从会话中存储的用户 ID 重新加载用户对象。
# 它应该接受一个用户的 unicode ID 作为参数，并且返回相应的用户对象。
# 如果 ID 无效的话，它应该返回 None (而不是抛出异常)。(在这种情况下，ID 会被手动从会话中移除且处理会继续)
@loginmanager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    title = db.Column(db.String(240), index=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.Date, index=True, default=date.today)
    views = db.Column(db.Integer, default=0)
    tags = db.relationship('Tag', secondary='marks', backref=db.backref('posts', lazy='dynamic'), lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        import forgery_py
        from random import seed, randint
        seed()
        for i in range(count):
            tags = Tag.query.limit(3).all()
            category = Category.query.all()
            post = Post(
                category=category[randint(0, len(category) - 1)],
                title=forgery_py.lorem_ipsum.title(),
                content=forgery_py.lorem_ipsum.paragraphs(),
                timestamp=forgery_py.date.date(True),
                tags=tags
            )
            db.session.add(post)
            db.session.commit()

    def __repr__(self):
        print '<Post %r>' % self.title


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)

    def __repr__(self):
        print '<Tag %r>' % self.name

marks = db.Table('marks',
                db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
                )


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    def __repr__(self):
        print '<Category %r>' % self.name


class MicroPost(db.Model):
    __tablename__ = 'microposts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        for i in range(count):
            post = MicroPost(
                content=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                timestamp=forgery_py.datetime.datetime(True)
            )
            db.session.add(post)
            db.session.commit()

    def __repr__(self):
        print '<MicroPost %r>' % self.content


