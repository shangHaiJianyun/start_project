import re
import random

from flask import jsonify, request, current_app, g, render_template, abort, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_security import current_user, forms, auth_token_required, login_required
from flask_security.utils import login_user, logout_user

from api.common_func.decorators import admin_required, roles_required
from api.common_func.get_role import get_user_role
from api.models.models import *
from api.modules.user import user_blu


# 主界面的显示
@user_blu.route("/")
@user_blu.route("/index")
@login_required
@jwt_required
def index():
    user = current_user
    # user = get_jwt_identity()
    u = row2dict(user)
    # return jsonify(user)
    return jsonify(u)


# 用户登陆
@user_blu.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    try:
        user = User.query.filter_by(username=username).first()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(msg="db error")
    if not user:
        return jsonify(msg='Not found this user')
    if user.check_password(password):
        token = create_access_token(identity=username)
        login_user(user)
        # print(token)
        # print(user.roles)
        data = {
            "token": token,
            'username': user.username,
            "user_role": str(user.roles)
        }
        # print("密码成功")
        return jsonify(data)
    else:
        return jsonify(msg="Password error")


# 用户登出
@user_blu.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(msg='user logout')


# 添加新用户，只有Admin角色才可进行操作
@user_blu.route('/add_user', methods=['POST'])
@login_required
@admin_required
def add_user():
    # 定义装饰器admin_required管理操作权限
    username = request.json.get('username')
    password = request.json.get('password')
    user = user_datastore.create_user(username=username, password=password)
    user.set_password()
    user_role = get_user_role('User')
    user_datastore.add_role_to_user(user, user_role)
    user.mobile = username
    db.session.commit()

    return jsonify(msg='add success')


# 修改并更新用户资料
@user_blu.route('/update_info', methods=['POST'])
@login_required
def update_info():
    # 获取需要的参数
    name = request.json.get('name')
    email = request.json.get('email')
    mobile = request.json.get('mobile')
    # 校验参数的完整性
    if not all([mobile, name, email]):
        return jsonify(msg='please check your parameters')
    # 校验邮箱格式
    if not re.match('[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$',email):
        return jsonify(msg='wrong email')
    # 校验手机号格式
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(msg='illegal mobile')

    # 修改用户信息
    current_user.name = name
    current_user.email = email
    current_user.mobile = mobile
    db.session.commit()

    return jsonify(row2dict(current_user))


# 获取短信验证码
@user_blu.route('/get_sms_code', methods=['POST'])
@login_required
def get_sms_code():
    # 获取参数
    mobile = request.json.get("mobile")
    # 校验参数
    if mobile != current_user.mobile:
        return jsonify(msg='parameter error')

    # 校验手机号格式
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(msg='pattern error')

    # 根据图片key取出验证码文字
    # try:
    #     real_img_code = sr.get("img_code_id_" + img_code_id)
    # except BaseException as e:
    #     current_app.logger.error(e)
    #     return jsonify(msg='db error)

    # 如果校验成功, 发送短信
    # 生成4位随机数字
    sms_code = "%04d" % random.randint(0, 9999)
    current_app.logger.info("短信验证码为: %s" % sms_code)
    # res_code = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # if res_code == -1:  # 短信发送失败
    #     return jsonify(msg='send failed')

    # # 将短信验证码保存到redis
    # try:
    #     sr.set("sms_code_id_" + mobile, sms_code, ex=60)
    # except BaseException as e:
    #     current_app.logger.error(e)
    #     return jsonify(msg=' db error')
    # 将短信发送结果使用json返回
    return jsonify(msg='ok')


# 修改密码/需要手机号短信验证
@user_blu.route('/change_pwd', methods=['GET', 'POST'])
@login_required  # 只有登录的人才能修改密码
def change_password():
    # 获取参数
    mobile = request.json.get('mobile')
    sms_code = request.json.get('sms_code')
    new_password = request.json.get('password')

    # 校验手机号格式
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(msg='error mobile')

    # 根据手机号取出短信验证码文字
    # try:
    #     real_sms_code = sr.get("sms_code_id_" + mobile)
    # except BaseException as e:
    #     current_app.logger.error(e)
    #     return jsonify(msg='db error')
    # # 校验图片验证码
    # if not real_sms_code:  # 校验是否已过期
    #     return jsonify(msg='sms_coe expired')
    #
    # if sms_code != real_sms_code:  # 校验验证码是否正确
    #     return jsonify(msg='error sms_code')
    current_user.password = new_password
    current_user.set_password()
    db.session.commit()
    return jsonify(msg='modify success')


# token携带后验证
@user_blu.route('/protected', methods=['GET'])
# @jwt_required
# @admin_required
@roles_required('User')
def token_protected():
    this_user = get_jwt_identity()
    return jsonify(logged_in_as=this_user), 200
    # return 'you\'re logged in by Token!'