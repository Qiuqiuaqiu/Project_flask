from flask import render_template, g, abort, current_app

from info import constants
from info.models import News
from info.modules.news import news_blu
from info.utils.common import user_login


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

    # 详情页收藏和已收藏是由is_collected
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