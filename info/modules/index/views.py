from info.models import User
from info.modules.index import index_blu

from info import redis_store
from flask import session, render_template, redirect, current_app


@index_blu.route('/')
def index():
    user_id = session.get("user_id",None)
    if user_id:
        try:
            user = User.query.filter(User.id==user_id)
        except Exception as e:
            current_app.logger.error(e)

    data = {
        "user", user.to_dict() if user else None
    }

    return render_template("news/index.html",data=data)

@index_blu.route('/favicon.ico')
def favicon():
    # return redirect("/static/news/favicon.ico")
    return current_app.send_static_file("news/favicon.ico")