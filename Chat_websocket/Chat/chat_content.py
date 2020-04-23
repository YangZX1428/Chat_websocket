from flask import render_template, request, flash, redirect,Blueprint
from Chat.forms import SearchForm
"""
处理主页面和错误界面
"""
main = Blueprint("main",__name__)

@main.route('/index', methods=["POST", "GET"])
def index():
    form = SearchForm()
    if request.args.get("quit"):
        flash("您已成功退出聊天室!")
    if form.validate_on_submit():
        key = form.url.data
        return redirect(key)
    return render_template("home.html", form=form)


@main.errorhandler(404)
def error(e):
    return "404 Page !"
