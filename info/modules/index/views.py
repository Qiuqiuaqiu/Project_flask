from info.modules.index import index_blu

from info import redis_store
from flask import session, render_template, redirect, current_app


@index_blu.route('/')
def index():
    redis_store.set('name','laowang')
    session["xiaohua"] = 'xiaohua'
    return render_template("news/index.html")

@index_blu.route('/favicon.ico')
def favicon():
    # return redirect("/static/news/favicon.ico")
    return current_app.send_static_file("news/favicon.ico")