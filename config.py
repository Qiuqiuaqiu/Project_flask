import logging
from redis import StrictRedis


class Config(object):
    SECRET_KEY = '123131'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/project_flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 给配置类里自定义两个属性
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 指定session的存储方式
    SESSION_TYPE = "redis"
    # 指定session的储存对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    # 设置session签名　加密
    SESSION_USE_SIGNER = True
    # 设置session永久保存
    SESSION_PERMANENT = False
    # 设置session保存时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2

class DevelopConfig(Config):
    logging_level = logging.DEBUG
    pass

class ProductConfig(Config):
    logging_level = logging.WARNING
    DEBUG = False


class TestingConfig(Config):
    pass

configs = {
    'develop' : DevelopConfig,
    'product' : ProductConfig,
    'testing' : TestingConfig

}