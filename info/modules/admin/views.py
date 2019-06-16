import datetime

from flask import render_template, request, current_app, session, redirect, url_for, g, jsonify

from info import user_login, constants
from info.models import User, News
from info.modules.admin import admin_blu
from info.utils.response_code import RET


@admin_blu.route('/news_review_action', methods=["POST"])
def news_review_action():
    # 1. 接受参数
    news_id = request.json.get("news_id")  # ""
    action = request.json.get("action")

    # 2. 参数校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询到指定的新闻数据
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    if action == "accept":
        # 代表接受
        news.status = 0
    else:
        # 代表拒绝
        reason = request.json.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="请输入拒绝原因")
        news.status = -1
        news.reason = reason

    return jsonify(errno=RET.OK, errmsg="OK")


@admin_blu.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):

    # 通过id查询新闻
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return render_template('admin/news_review_detail.html', data={"errmsg": "未查询到此新闻"})

    # 返回数据
    data = {"news": news.to_dict()}
    return render_template('admin/news_review_detail.html', data=data)


@admin_blu.route('/news_review')
def news_review():

    page = request.args.get("p", 1)
    keywords = request.args.get("keywords")

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1

    # 如果有关键字  添加查询条件：该条新闻中的titile包含该关键字就可以了
    # 如果没有关键字  还是用原来的条件 News.status != 0
    # 如果有不同的查询，只有条件不一样。
    filters = [News.status != 0]
    if keywords:
        filters.append(News.title.contains(keywords))

    try:
        paginate = News.query.filter(*filters) \
            .order_by(News.create_time.desc()) \
            .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    context = {"total_page": total_page,
               "current_page": current_page,
               "news_list": news_dict_list}

    return render_template('admin/news_review.html', data=context)


@admin_blu.route("/user_list")
def user_list():
    """
    所有用户列表
    :return:
    """
    page = request.args.get("page", 1)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    users = []
    current_page = 1
    total_page = 1

    try:
        paginate = User.query.filter(User.is_admin == False).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 进行模型列表转字典列表
    user_dict_li = []
    for user in users:
        user_dict_li.append(user.to_admin_dict())

    data = {
        "users": user_dict_li,
        "total_page": total_page,
        "current_page": current_page,
    }

    return render_template("admin/user_list.html", data=data)


@admin_blu.route("/user_count")
def user_count():

    # 一、用户总数
    total_count = User.query.filter(User.is_admin == False).count()

    t = datetime.datetime.now()
    # 二、月新增数   距今天一个月
    # 1、找到一个"2019-03-01"的时间对象 必须先获取一个今天的时间对象
    # datetime.datetime.now()
    # 2、制造时间字符串"2019-03-01"
    month_date_str = "%d-%02d-01" % (t.year, t.month)
    month_date = datetime.datetime.strptime(month_date_str, "%Y-%m-%d")
    month_count = User.query.filter(User.is_admin == False, User.create_time > month_date).count()

    # 三、日新增数
    day_date_str = "%d-%02d-%02d" % (t.year, t.month, t.day)
    day_date = datetime.datetime.strptime(day_date_str, "%Y-%m-%d")
    day_count = User.query.filter(User.is_admin == False, User.create_time > day_date).count()

    # 四、用户活跃数统计
    # ["2019-02-08", "2019-02-09", ......]
    # [100, 200, ......]
    # 1、先查询出今天的登录用户总数   何为今天？？？ 2019-03-10:0:0:0 <= last_login < 2019-03-11:0:0:0
    # 2、找2019-03-10的时间对象
    activate_date = []
    activate_count = []
    for i in range(0, 31):
        start_date = day_date - datetime.timedelta(days=i-0)  # 2019-03-10 2019-03-07 2019-03-06
        end_date = day_date - datetime.timedelta(days=i-1)  # 2019-03-11 2019-03-08  2019-03-07
        count = User.query.filter(User.is_admin == False,
                                  User.last_login >= start_date,
                                  User.last_login < end_date).count()
        start_date_str = start_date.strftime("%Y-%m-%d")
        activate_date.append(start_date_str)
        activate_count.append(count)

    activate_count.reverse()
    activate_date.reverse()

    data = {
        "total_count": total_count,
        "month_count": month_count,
        "day_count": day_count,
        "activate_date": activate_date,
        "activate_count": activate_count
    }

    return render_template("admin/user_count.html", data=data)


@admin_blu.route("/index")
@user_login
def index():
    """
    首页逻辑
    :return:
    """
    data = {
        "user_info": g.user.to_dict()
    }
    return render_template("admin/index.html", data=data)


@admin_blu.route("/login", methods=["GET", "POST"])
def login():
    """
    渲染后台登录界面
    :return:
    """
    if request.method == "GET":
        # 在get请求中，先从session中取user_id 和 is_admin 如果能取到，直接重定向到首页
        user_id = session.get("user_id")
        is_admin = session.get("is_admin")
        if user_id and is_admin:
            return redirect(url_for("admin.index"))
        return render_template("admin/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template("admin/login.html", errmsg="请输入用户名或者密码")

    try:
        user = User.query.filter(User.mobile == username, User.is_admin == 1).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="用户查询失败")

    if not user:
        return render_template("admin/login.html", errmsg="用户未注册")

    if not user.check_passowrd(password):
        return render_template("admin/login.html", errmsg="用户名或密码输入错误")

    session["user_id"] = user.id
    session["is_admin"] = user.is_admin

    return redirect(url_for("admin.index"))