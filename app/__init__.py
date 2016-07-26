# coding: utf-8
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from wechat_sdk import WechatConf, WechatBasic
from wechat_sdk.exceptions import OfficialAPIError


# 应用初始化
app = Flask(__name__)
app.debug = True
app.config.from_object('config')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'alibaba'
bootstrap = Bootstrap(app)


# wechat部分初始化
def refresh_access_token():
    # 刷新access_token
    try:
        at = wechat.get_access_token()
        app.config['WECHAT_ACCESS_TOKEN'] = at['access_token']
        app.config['WECHAT_ACCESS_TOKEN_EXPIRES_AT'] = at['access_token_expires_at']
    except OfficialAPIError as e:
        print "'errcode:' %s \n errmsg: %s" % (e.errcode, e.errmsg)

conf = WechatConf(
    token=app.config['WECHAT_TOKEN'],
    appid=app.config['WECHAT_APPID'],
    appsecret=app.config['WECHAT_APPSECRET'],
    encrypt_mode='compatible',
    access_token=app.config['WECHAT_ACCESS_TOKEN'],
    access_token_expires_at=app.config['WECHAT_ACCESS_TOKEN_EXPIRES_AT']
)
wechat = WechatBasic(conf=conf)
# refresh_access_token()

from . import views

