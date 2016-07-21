# coding: utf-8
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

# 应用初始化
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'cptbtptpBcptDtptp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@127.0.0.1:3306/personal_website?charset=utf8'
db = SQLAlchemy(app)
loginmanager = LoginManager(app)
bootstrap = Bootstrap(app)


from . import views
