from flask import Blueprint


admin_blu = Blueprint("admin", __name__, url_prefix="/admin")


from .views import *

@admin_blu.before_request
def admin_identification():
    # 我先从你的session获取下is_admin 如果能获取到 说明你是管理员
    # 如果访问的接口是/admin/login 那么可以直接访问
    is_login = request.url.endswith("/login")  # 判断请求的url是否已/login结尾
    is_admin = session.get("is_admin")  # 判断用户是否为管理员
    if not is_admin and not is_login:
        return redirect("/")