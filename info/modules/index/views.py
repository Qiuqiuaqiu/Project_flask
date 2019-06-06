from info.modules.index import index_blu
import logging
from info import redis_store

@index_blu.route('/')
def index():
    redis_store.set('name','laowang')
    return 'index'