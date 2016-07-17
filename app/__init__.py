# coding: utf-8
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 应用初始化
app = Flask(__name__)
app.debug = True
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'cptbtptpBcptDtptp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@127.0.0.1:3306/' + os.path.join(basedir, 'db') + '?charset=utf8'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:\\database'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@127.0.0.1:3306/personal_website?charset=utf8'
db = SQLAlchemy(app)
loginmanager = LoginManager(app)


from . import views
