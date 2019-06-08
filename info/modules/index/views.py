from info.modules.index import index_blu

from info import redis_store
from flask import session

@index_blu.route('/')
def index():
    redis_store.set('name','laowang')
    session["xiaohua"] = 'xiaohua'
    return 'index'