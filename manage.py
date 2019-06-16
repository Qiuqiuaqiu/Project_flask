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

from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

from info import create_app,db
# 导入数据表
from info import models

app = create_app("develop")

# 六、配置Manager
manager = Manager(app)
# 七、配置Migrate
Migrate(app,db)
manager.add_command('db',MigrateCommand)


if __name__ == '__main__':
    # print(app.url_map)
    print(1234)
    manager.run()