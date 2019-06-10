from datetime import datetime
import random
import re
from flask import request, abort, current_app, make_response, json, jsonify, session
from info import redis_store, constants, db
from info.models import User
from info.modules.passport import passport_blu
from info.response_code import RET
from info.utils.captcha.captcha import captcha
from info.libs.yuntongxun.sms import CCP
from werkzeug.security import generate_password_hash

# １、请求的方式是什么
# ２、请求的url是什么
# ３、参数的名字是什么
# ４、返回给前端的参数和参数类型是什么
@passport_blu.route("/sms_code",methods=["POST"])
def get_sms_code():
    # 1、接收参数：modile, image_code, image_code_id
    # 2、校检参数mobile
    # ３、校验用户输入的验证码和通过image_code_id查询出来的验证码是否一致
    # ４、定义一个６位随机码
    # ５、调用云通讯发送手机验证码
    # ６、将验证码保存到redis
    # ７、给前端一个响应
    # json_data = request.data
    # dict_data = json.loads(json_data)


    dict_data = request.json
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    if not re.match(r"1[35678]\d{9}",mobile):
        return jsonify(erron=RET.PARAMERR,errmsg="手机号格式不正确")

    try:
        real_image_code = redis_store.get("ImageCodeId_"+ image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="数据库查询失败")

    if not real_image_code:
        return jsonify(erron=RET.NODATA,errmsg="图片验证码已过期")

    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR,errmsg="图片验证码输入错误")

    sms_code_str = "%06d" % random.randint(0,999999)
    print(sms_code_str)

    # result = CCP().send_template_sms(mobile,[sms_code_str,5],1 )
    #
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR,errmsg="第三方错误")
    try:
        redis_store.setex("sms_"+mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code_str)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="手机验证码保存失败")

    return jsonify(errno=RET.OK,errmsg="发送成功")

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
        print(text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response

@passport_blu.route("/register",methods=["POST"])
def register():
    # 1、接收参数
    # ２、判断是否完整参数
    # ３、判断参数
    # ４、放入数据库
    # ５、状态保持

    dict_data = request.json
    mobile = dict_data.get("mobile")
    smscode = dict_data.get("smscode")
    password = dict_data.get("password")

    if not all([mobile,smscode,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")

    if not re.match(r"1[35678]\d{9}",mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    try:
        real_sms_code = redis_store.get("sms_"+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    if smscode != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="手机验证码错误")

    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.password_hash = generate_password_hash(password)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库存储错误")

    session["user_id"] = user.id
    session["mobile"] = mobile
    session["nike_name"] = user.nick_name

    return jsonify(errno=RET.OK,errmsg="注册成功")

@passport_blu.route("/login" ,methods=["POST"])
def login():
    # 1、取到参数
    # ２、判断参数
    # ３、状态保持


    dict_data = request.json

    mobile = dict_data.get("mobile")
    password = dict_data.get("passport")

    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")

    if not re.match(r"1[35678]\d{9}",mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not user:
        return jsonify(errno=RET.DATAERR, errmsg="未找到此用户")

    if not user.check_passowrd(password):
        return jsonify(errno=RET.DATAERR, errmsg="密码错误")

    session["user_id"] = user.id
    session["user_name"] = user.nick_name
    session["mobile"] = user.mobile

    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        db.rollback()
        current_app.logger.error(e)

    return jsonify(errno=RET.OK,errmsg="登录成功")

@passport_blu.route('/logout')
def logout():
    session.pop("user_id",None)
    session.pop("mobile",None)
    session.pop("nike_name",None)
    return jsonify(errno=RET.OK,errmsg="退出成功")
