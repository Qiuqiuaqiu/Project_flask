"""
１、集成配置类
２、集成sqlalchemy到flask
3、集成redis　可以把容易变化的值放入到配置中
4、CSRFprotect
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect


# 创建配置类
class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:127.0.0.1@3306/project_flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 给配置类里自定义两个属性
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
# 集成redis
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

CSRFProtect(app)

@app.route('/')
def index():
    redis_store.set('name','xiaohua')
    return 'index'

if __name__ == '__main__':
    app.run(debug=True)