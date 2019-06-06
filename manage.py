"""
１、集成配置类
２、集成sqlalchemy到flask
3、集成redis　可以把容易变化的值放入到配置中
4、CSRFprotect
5、集成session
6、集成Manager
7、集成
8、集成migrate
"""

from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand


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
# 六、配置Manager
manager = Manager(app)
# 七、配置Migrate
Migrate(app,db)
manager.add_command('db',MigrateCommand)

@app.route('/')
def index():
    session['name'] = '笑话'
    return 'index'

if __name__ == '__main__':
    manager.run()