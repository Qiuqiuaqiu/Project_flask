from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_session import Session

from config import configs

db = SQLAlchemy()
def create_app(config_name):
    app = Flask(__name__)
    # 一、集成配置类
    app.config.from_object(configs[config_name])
    # 二、集成salalchemy
    db.init_app(app)
    # 三、集成redis
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST,port=configs[config_name].REDIS_PORT)
    # 四、集成csrf
    CSRFProtect(app)
    # 五、集成session
    Session(app)

    return app