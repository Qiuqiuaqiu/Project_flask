"""
１、集成配置类
２、集成sqlalchemy到flask
3、集成redis　可以把容易变化的值放入到配置中
4、CSRFprotect
5、集成session
"""

from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
# 创建配置类

class Config(object):
    SECRET_KEY = '123131'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:127.0.0.1@3306/project_flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 给配置类里自定义两个属性
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 指定session的存储方式
    SESSION_TYPE = 'redis'
    # 指定session的储存对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    # 设置session签名　加密
    SESSION_USE_SIGNER = True
    # 设置session永久保存
    SESSION_PERMANENT = False
    # 设置session保存时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2

app = Flask(__name__)
# 一、集成配置类
app.config.from_object(Config)
# 二、集成salalchemy
db = SQLAlchemy(app)
# 三、集成redis
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
# 四、集成csrf
CSRFProtect(app)
# 五、集成session
Session(app)

@app.route('/')
def index():
    session['name'] = '笑话'
    return 'index'

if __name__ == '__main__':
    app.run(debug=True)