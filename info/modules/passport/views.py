from flask import request, abort, current_app, make_response
from info import redis_store, constants
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha

@passport_blu.route('/image_code')
def get_image_code():
    """
    1、接受参数
    ２、校对参数是否存在
    ３、生成验证码
    ４、把随机的字符串和生成的文本文档以key,value形式存入redis
    5、返回图片
    """
    image_code_id = request.args.get("imageCodeId")
    if not image_code_id:
        abort(404)
    _,text,image = captcha.generate_captcha()

    try:
        redis_store.setex("ImageCodeId_"+ image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        current_app.logging.error(e)
        abort(500)
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response