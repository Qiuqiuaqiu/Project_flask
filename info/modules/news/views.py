from info import constants, db
from info.models import User, News, Comment, CommentLike
from info.modules.news import news_blu
from flask import render_template, session, current_app, g, abort, jsonify, request

from info.utils.common import user_login
from info.utils.response_code import RET


@news_blu.route('/<int:news_id>')
@user_login
def news_detail(news_id):
    '''新闻详情页'''

    # 查询用户是否已经登录
    user = g.user

    print(111111)

    # 右侧的新闻排列的逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())
    # 查询新闻数据
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        abort(404)

    # 更新新闻点击的次数
    news.clicks += 1

    # 查询该用户是否收藏了该新闻
    is_collected = False
    if user:
        if news in user.collection_news:
            is_collected = True

    # 查询评论数据按照创建时间倒序排
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.error(e)

    # coment_like_ids也定义到前边，要不然，如果if g.user进不去。那么下边for中就不能用comment_like_ids
    comment_like_ids = []

    if g.user:
        # 查询当前用户的所有评论
        comment_ids = [comment.id for comment in comments]
        # 在查询当前评论中哪些评论被当前登录用户所点赞
        comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                 CommentLike.user_id == g.user.id).all()
        # 取到所有被点赞的评论id
        comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]

    comment_dict_li = []
    # 组装查询出来的评论
    for comment in comments:
        comment_dict = comment.to_dict()

        # 代表没有点赞
        comment_dict["is_like"] = False
        # 判断当前遍历到的评论是否被当前登录用户所点赞
        if comment.id in comment_like_ids:
            comment_dict['is_like'] = True

        comment_dict_li.append(comment_dict)

    is_followed = False
    # 新闻存在作者，且当前已经有用户登录
    if news.user and user:
        # 检查当前user是否关注过这个新闻的作者
        if news.user in user.followed:
            is_followed = True

    # 查询新闻作者已经通过审核的新闻文章篇数
    news_count = News.query.filter(News.user_id == news.user_id, News.status == 0).count()

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        "news": news.to_dict(),
        "is_collected": is_collected,
        "comments": comment_dict_li,
        "is_followed": is_followed,
        "news_count": news_count
    }
    return render_template('news/detail.html', data=data)


@news_blu.route('/news_collect', methods=["POST"])
@user_login
def collect_news():
    '''收藏新闻'''
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="User is not logged in！")

    # 接受参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 判断参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter error！")

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter error！")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter error！")

    # 查询新闻并判断新闻是否存在，确保不会出错
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.DBERR, errmsg="Data query error！")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="No data is queried！")
    # 收藏以及取消收藏
    if action == "cancel_collect":
        if news in user.collection_news:
            # 删除
            user.collection_news.remove(news)
    else:
        if news not in user.collection_news:
            user.collection_news.append(news)

    return jsonify(errno=RET.OK, errmsg="Successful collection operation！")


@news_blu.route('/news_comment', methods=["POST"])
@user_login
def comment_news():
    '''评论新闻或者回复某条新闻下指定的评论'''
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="User is not logged in！")
    # 获取请求参数
    news_id = request.json.get("news_id")
    comment_content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    # 判断参数 不判断parent_id是因为在自己发表评论的时候，不需要parent_id
    if not all([news_id, comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter error！")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter error！")
    # 查询新闻，判断新闻是否存在
    try:
        news = News.query.get(news_id)

    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.DBERR, errmsg="Data query error！")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="No data is queried！")

    # 初始化一个评论模型 并赋值
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id

    try:
        # 这里需要自己commit是因为在return的时候能用到comment里面的数据，如果用不到可以不用commit，让sqlalchemy在return以后帮我们
        # 自动提交
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict())


@news_blu.route('/comment_like', methods=['POST'])
@user_login
def comment_like():
    '''评论点赞'''
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="User is not logged in！")

    # 获取参数
    comment_id = request.json.get("comment_id")
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 校验参数
    if not all([comment_id, news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter error！")
    if action not in ['add', 'remove']:
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter error！")
    try:
        comment_id = int(comment_id)
        news_id = int(news_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='Parameter error！')
    try:
        comment = Comment.query.get(comment_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Data query error！")

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="No data is queried！")

    if action == 'add':
        comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,
                                                      CommentLike.comment_id == comment.id).first()
        if not comment_like_model:
            comment_like_model = CommentLike()
            comment_like_model.user_id = user.id
            comment_like_model.comment_id = comment.id
            # 数据库增加一条点赞数量
            comment.like_count += 1
            db.session.add(comment_like_model)

    else:
        # 取消点赞
        comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,
                                                      CommentLike.comment_id == comment.id).first()
        if comment_like_model:
            db.session.delete(comment_like_model)
            # 数据库减少一条点赞记录
            comment.like_count -= 1

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="Data save failed！")
    return jsonify(errno=RET.OK, errmsg="OK")


@news_blu.route('/followed_user', methods=["POST"])
@user_login
def followed_user():
    """关注/取消关注用户"""
    if not g.user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    user_id = request.json.get("user_id")
    action = request.json.get("action")

    if g.user.id == int(user_id):
        return jsonify(errno=RET.REQERR, errmsg="不能关注自己")

    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("follow", "unfollow"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询到关注的用户信息
    try:
        target_user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库失败")

    if not target_user:
        return jsonify(errno=RET.NODATA, errmsg="未查询到用户数据")

    # 根据不同操作做不同逻辑
    if action == "follow":
        if target_user.followers.filter(User.id == g.user.id).count() > 0:
            return jsonify(errno=RET.DATAEXIST, errmsg="当前已关注")
        target_user.followers.append(g.user)
    else:
        if target_user.followers.filter(User.id == g.user.id).count() > 0:
            target_user.followers.remove(g.user)

    # 保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存错误")

    return jsonify(errno=RET.OK, errmsg="操作成功")
