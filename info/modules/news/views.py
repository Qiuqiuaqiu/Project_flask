from flask import render_template, g, abort, current_app, jsonify, request

from info import constants, db
from info.models import News, Comment
from info.modules.news import news_blu
from info.response_code import RET
from info.utils.common import user_login

@news_blu.route("/news_collect", methods=["POST"])
@user_login
def news_collect():
    """
    新闻收藏和取消收藏功能
    1、接收参数
    2、校验参数
    3、收藏新闻和取消收藏
    4、返回响应
    :return:
    """
    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    news_id = request.json.get("news_id")
    action = request.json.get("action")

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="数据格式不正确")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该条新闻不存在")

    # 执行具体业务逻辑了
    if action == "collect":
        # 当我们去收藏一条新闻的时候，我们应该先去判断该用户书否收藏过该条新闻，如果没有收藏过，才去添加
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        # 当我们去取消收藏的时候，如果该新闻在你的收藏列表中，才去删除
        if news in user.collection_news:
            user.collection_news.remove(news)

    return jsonify(errno=RET.OK, errmsg="OK")

@news_blu.route("/<int:news_id>")
@user_login
def detail(news_id):
    """
    详情页面渲染
    :param news_id:
    :return:
    """
    # 1、查询点击排行新闻
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(
            constants.CLICK_RANK_MAX_NEWS).all()  # [obj, obj, obj]
    except Exception as e:
        current_app.logger.error(e)

    # [obj, obj, obj] --> [{}, {}, {}, {}]
    clicks_news_li = [news.to_basic_dict() for news in clicks_news]

    # 2、显示新闻的具体信息
    # 判断新闻id存不存在
    if not news_id:
        abort(404)
    # 判断新闻id是不是整数类型
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    # 判断新闻是不是存在
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        abort(404)

    news.clicks += 1

    user = g.user

    is_collected = False
    # 在什么样的一个情况下  is_collected = True
    # 需求：如果 该用户收藏了该条新闻 is_collected = True
    # 1、保证用户存在
    # 2、新闻肯定存在
    # 3、该条新闻在用户收藏新闻的列表中
    # 4、用户收藏新闻的列表----> user.collection_news.all()  [news, news]
    if user and news in user.collection_news.all():
        is_collected = True



    data = {
        "user_info": user.to_dict() if user else None,
        "clicks_news_li": clicks_news_li,
        "news": news.to_dict(),
        "is_collected": is_collected
    }
    return render_template("news/detail.html",data=data)

@news_blu.route("/news_comment",methods=["POST"])
@user_login
def news_comment():
    """
    新闻评论功能
    １、接收参数　用户　新闻　评论内容　parent_id
    ２、校检参数
    ３、业务逻辑　往数据库添加一条评论
    ４、返回响应　返回响应的评论
    """

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户不存在")

    news_id = request.json.get("news_id")
    comment_str = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    if not all([news_id,comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该条新闻不存在")

    comment = Comment()
    comment.news_id = news.id
    comment.user_id = user.id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库存储失败")

    return jsonify(errno=RET.OK, errmsg="ok", data=comment.to_dict())


