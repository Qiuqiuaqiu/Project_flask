import datetime

from flask import render_template, request, current_app, session, redirect, url_for, g

from info import user_login
from info.models import User
from info.modules.admin import admin_blu


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