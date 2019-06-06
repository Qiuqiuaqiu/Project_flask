from info.modules.index import index_blu
import logging

@index_blu.route('/')
def index():
    logging.debug('debug')
    logging.warning('warning')
    logging.fatal('fatal')
    logging.error('error')
    logging.critical('critical')
    return 'index'