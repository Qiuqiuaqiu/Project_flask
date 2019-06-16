from flask import g, jsonify, redirect, render_template, request, current_app

from info import db
from info.modules.profile import profile_blu
from info.response_code import RET
from info.utils.common import user_login


@profile_blu.route("/info")
@user_login
def user_info():

    user = g.user

    if not user:
        return redirect("/")

    data = {
        "user": user.to_dict()

    }
    return render_template("news/user.html",data=data)

@profile_blu.route("/user_base_info",methods=["GET","POST"])
@user_login
def user_base_info():

    user = g.user

    if request.method == "GET":
        data = {
            "user": user.to_dict()
        }


        return render_template("news/user_base_info.html",data=data)
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存错误")

    return jsonify(errno=RET.OK, errmsg="Ok", data=user.to_dict())


