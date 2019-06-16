from flask import g, jsonify, redirect, render_template

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
        "user_info": user.to_dict()

    }
    return render_template("news/user.html",data=data)