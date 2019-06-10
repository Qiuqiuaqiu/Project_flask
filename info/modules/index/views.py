from info.models import User, News
from info.modules.index import index_blu

from info import redis_store
from flask import session, render_template, redirect, current_app


@index_blu.route('/')
def index():
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.filter(User.id==user_id).first()
        except Exception as e:
            current_app.logger.error(e)

    new_list = []
    try:
        new_list = News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)

    new_dict_li = []
    for news in new_list:
        new_dict_li.append(news.to_basic_dict())

    data = {
        "user": user.to_dict() if user else None,
        "new_dict_li": new_dict_li
    }

    return render_template("news/index.html",data=data)

@index_blu.route('/favicon.ico')
def favicon():
    # return redirect("/static/news/favicon.ico")
    return current_app.send_static_file("news/favicon.ico")