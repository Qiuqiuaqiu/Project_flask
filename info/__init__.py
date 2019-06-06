from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_session import Session

from config import config

app = Flask(__name__)
# 一、集成配置类
app.config.from_object(config['develop'])
# 二、集成salalchemy
db = SQLAlchemy(app)
# 三、集成redis
redis_store = StrictRedis(host=config['develop'].REDIS_HOST,port=config['develop'].REDIS_PORT)
# 四、集成csrf
CSRFProtect(app)
# 五、集成session
Session(app)