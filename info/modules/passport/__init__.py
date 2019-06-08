from flask import Blueprint

passport_blu = Blueprint("passport_blu",__name__,url_prefix='/passport')

from .views import passport_blu