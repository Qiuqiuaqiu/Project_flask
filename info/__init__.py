from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect,generate_csrf
from redis import StrictRedis
from flask_session import Session
import logging
from config import configs


db = SQLAlchemy()
def set_log(config_name):
    logging.basicConfig(level=configs[config_name].logging_level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

redis_store = None #type: StrictRedis

def create_app(config_name):

    set_log(config_name)

    app = Flask(__name__)
    # 一、集成配置类
    app.config.from_object(configs[config_name])
    # 二、集成salalchemy
    db.init_app(app)
    # 三、集成redis
    global redis_store
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST,port=configs[config_name].REDIS_PORT,decode_responses=True)
    # 四、集成csrf
    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token", csrf_token)
        return response

    CSRFProtect(app)
    # 五、集成session


    Session(app)
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    return app

