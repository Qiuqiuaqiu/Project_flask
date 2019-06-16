from flask import render_template, current_app, session, request, jsonify, g

from info import redis_store, constants
from info.models import User, News, Category
from info.utils.common import user_login
from info.utils.response_code import RET
from . import index_blu


@index_blu.route('/')
@user_login
def index():
    '''显示首页'''
    # 如果用户已经登录，将当前登录的用户数据传到模版中，供模版显示

    user = g.user
    # 右侧新闻排行的逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    categories = Category.query.all()
    category_li = []
    for category in categories:
        category_li.append(category.to_dict())

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        "category_li": category_li
    }

    return render_template('news/index.html', data=data)


@index_blu.route('/favicon.ico')
def favicon():
    # send_static_file是flask查找静态文件所调用的方法
    return current_app.send_static_file('news/favicon.ico')


@index_blu.route('/news_list')
def news_list():
    '''获取首页新闻数据'''

    # 获取参数
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    # 默认不传递每夜新闻数量，默认为10条数据
    per_page = request.args.get("per_page", "10")

    # 校验参数
    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter error!")
    # 这里只显示审核通过的新闻
    filters = [News.status == 0]
    if cid != 1:  # 查询的不是最新的数据，数据库中不存在cid为1的分类
        # 需要添加条件
        filters.append(News.category_id == cid)

    # 查询数据
    try:
        # filter里面不加参数会查询全部数据
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(RET.DBERR, errmsg="Data query error！")

    # 取到当前页的数据
    news_model_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    # 将模型对象列表转换为字典列表
    news_dict_li = []
    for news in news_model_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_dict_li": news_dict_li
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)
