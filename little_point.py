# coding:utf-8

# models.py中，Post表与Tag表，多对多关系，给Post实例添加tags方法

from app.models import Tag, Post
from app import db
taglist = []
for tagname in taglist:
    tag = Tag()
    tag.tagname = tagname
    Post.tags.append(tag)
db.session.add(Post.tags)