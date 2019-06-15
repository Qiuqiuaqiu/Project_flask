from info.models import User, News, Category
from info.modules.index import index_blu

from info import redis_store
from flask import session, render_template, redirect, current_app, request, jsonify, g

from info.response_code import RET
from info.utils.common import user_login


@index_blu.route('/')
@user_login
def index():
    # 右上角逻辑实现
    # user_id = session.get("user_id")
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.filter(User.id==user_id).first()
    #     except Exception as e:
    #         current_app.logger.error(e)
    user = g.user
    # 点击排行逻辑实现
    new_list = []
    try:
        new_list = News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)
    new_dict_li = []
    for news in new_list:
        new_dict_li.append(news.to_basic_dict())
    # 显示新闻分类
    categories = Category.query.all()
    category_li = []
    for category in categories:
        category_li.append(category.to_dict())

    data = {
        "user_info": user.to_dict() if user else None,
        "clicks_news_li": new_dict_li,
        "categorys": category_li
    }

    return render_template("news/index.html",data=data)

@index_blu.route('/favicon.ico')
def favicon():
    # return redirect("/static/news/favicon.ico")
    return current_app.send_static_file("news/favicon.ico")

@index_blu.route('/news_list')
def get_new_list():

    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")

    if not all([cid,page,per_page]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")

    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.lagger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="数据类型错误")

    filters = []
    if cid != 1:
        filters.append(News.category_id==cid)

    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询错误")

    news_model_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page



    news_dict_list = [new.to_basic_dict() for new in news_model_list]

    data = {
        'total_page': total_page,
        'current_page': current_page,
        'news_dict_list': news_dict_list
    }

    print(news_dict_list,total_page,current_page)

    return jsonify(errno=RET.OK,errmsg="OK",data=data)

