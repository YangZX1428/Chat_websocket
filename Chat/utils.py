
from flask import redirect,request
# 该函数用于重定向到源界面
def redirect_back():
    return redirect(request.args.get("next", "index"))


