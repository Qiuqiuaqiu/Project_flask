from flask import g, jsonify, redirect, render_template, request, current_app

from info import db, constants
from info.libs.image_storage import storage
from info.models import Category, News
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

@profile_blu.route("/user_pic_info",methods=["GET","POST"])
@user_login
def user_pic_info():
    user = g.user
    if request.method == "GET":

        data = {
            "user": user.to_dict()
        }
        return render_template("news/user_pic_info.html",data=data)

    try:
        image_data = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        key = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    user.avatar_url = key

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="上传头像成功", data=constants.QINIU_DOMIN_PREFIX + key)

@profile_blu.route("/user_pass_info",methods=["GET","POST"])
@user_login
def user_pass_info():
    user = g.user

    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="密码错误")

    user.password = new_password

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")


    # return redirect("/")
    return jsonify(errno=RET.OK, errmsg="修改成功")

@profile_blu.route("/user_collection")
@user_login
def user_collection():
    """
    显示用户收藏的新闻
    :return:
    """
    user = g.user
    page = request.args.get("page")

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 查询该用户收藏的新闻
    news_list = [] # [obj, obj]
    current_page = 1
    total_page = 1
    try:
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = [news.to_dict() for news in news_list]

    data = {
        "news_dict_li": news_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template("news/user_collection.html", data=data)

@profile_blu.route("/user_news_release", methods=["GET", "POST"])
@user_login
def user_news_release():
    """
    发布新闻
    :return:
    """
    user = g.user
    if request.method == "GET":
        categorys = Category.query.all()  # [obj]

        categorys_dict_li = [category.to_dict() for category in categorys]

        categorys_dict_li.pop(0)

        data = {
            "categorys_dict_li": categorys_dict_li
        }
        return render_template("news/user_news_release.html", data=data)

    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        category_id = int(category_id)
        image_data = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型不正确")

    try:
        key = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="第三上传失败")

    # 执行业务逻辑
    news = News()
    news.title = title
    news.source = "个人发布"
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = user.id
    news.status = 1

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="OK")