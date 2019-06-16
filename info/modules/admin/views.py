from flask import render_template, request, current_app, session, redirect, url_for, g

from info.models import User
from info.modules.admin import admin_blu
from info.utils.common import user_login


@admin_blu.route("/login", methods=["GET","POST"])
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