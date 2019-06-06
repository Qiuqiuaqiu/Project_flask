from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_session import Session

from config import Config

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