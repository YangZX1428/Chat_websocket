from flask import Blueprint, render_template, flash, redirect, url_for
from Chat.utils import redirect_back
from flask_login import login_user
from Chat.forms import LoginForm, RegistForm
from Chat.models import User
"""
处理登录和注册视图的蓝图
"""
auth = Blueprint("auth", __name__)


@auth.route('/login', methods=["POST", "GET"])
def login():
    from Chat.app import db
    form = LoginForm()
    if form.validate_on_submit():
        username = form.name.data
        password = form.password.data
        if User.query.filter_by(username=username).first() is not None:
            admin = User.query.filter_by(username=username).first()
            if admin.check_pwd(password=password):
                login_user(admin, remember=False)
                admin.is_login = True
                db.session.commit()
                return redirect_back()
            else:
                flash("密码错误!")
        else:
            flash("用户名不存在!")
    return render_template("login.html", form=form)


@auth.route('/regist', methods=["POST", "GET"])
def regist():
    from Chat.app import db
    form = RegistForm()
    if form.validate_on_submit():
        username = form.name.data
        if not User.query.filter_by(username=username).first():
            u = User(username=username)
            u.set_password(form.password1.data)
            db.session.add(u)
            db.session.commit()
            flash("注册成功!")
            return redirect(url_for('login'))
        else:
            flash("该用户名已被使用")
    return render_template("regist.html", form=form)