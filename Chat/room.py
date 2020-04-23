
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify,session
room_bp = Blueprint("room_bp", __name__)
from flask_login import logout_user, current_user, login_required
from Chat.app import db, faker, ROOM_FACE_UPLOAD_PATH
from Chat.models import User, Room, AnonymousMessage, Message, AnonymousRoom
from Chat.utils import redirect_back
from Chat.forms import EditForm, RecordsSearchForm
import math
import random
import os
from flask_dropzone import random_filename
"""
定义了有关房间的视图
包括普通，匿名房间，加载更多聊天记录，设置虚拟用户名，头像，编辑房间，删除房间以及聊天记录
"""
get_more_page = 1
total_pages = 0
flag = 0

@room_bp.route('/logout')
@login_required
def logout():
    u = User.query.get(current_user.id)
    u.is_login = False
    db.session.commit()
    logout_user()
    flash("您已成功登出")
    return redirect(url_for("main.index"))


# 普通房间
@room_bp.route('/chat_page/<int:room_id>')
@login_required
def chat_page(room_id):
    global get_more_page, flag
    flag = 0
    get_more_page = 1
    r = Room.query.get(room_id)
    edit = 1 if request.args.get("edit") else 0
    author = User.query.get(r.create_user_id)
    if current_user._get_current_object() not in r.users:
        r.users.append(current_user._get_current_object())
    db.session.commit()
    messages = Message.query.with_parent(r).order_by(Message.timestamp.desc()).limit(8).all()
    messages = reversed(messages)
    return render_template("chat_page.html", r=r, messages=messages, author=author, edit=edit)


# 匿名房间
@room_bp.route("/chat_page/anonymous/<int:room_id>")
@login_required
def anonymous_room(room_id):
    global get_more_page
    get_more_page = 1
    if not request.args.get("permission", 0) or session.get("anony_name") is None:
        return redirect(url_for("room_bp.set_info", room_id=room_id))
    r = AnonymousRoom.query.get(room_id)
    u = User.query.get(r.create_user_id)
    messages = AnonymousMessage.query.with_parent(r).order_by(AnonymousMessage.timestamp.desc()).limit(8).all()
    messages = reversed(messages)
    return render_template("anonymous_room.html", r=r, author=u, anony_name=session.get("anony_name"), anony_face=session.get("anony_face"),
                           messages=messages)


# 普通房间获取更多历史消息
@room_bp.route("/get_more/<int:room_id>")
def get_more(room_id):
    global get_more_page, flag
    get_more_page += 1
    r = Room.query.get(room_id)
    total = Message.query.with_parent(r).count()
    total_pages = math.ceil(total / 8)
    if get_more_page <= total_pages:
        pagination = Message.query.with_parent(r).order_by(Message.timestamp.desc()).paginate(get_more_page, 8,
                                                                                              error_out=True)
        messages = pagination.items
        messages = reversed(messages)
        return jsonify(html=render_template("_more.html", messages=messages), total_pages=total_pages)
    return jsonify(total_pages=total_pages)


# 匿名房间获取更多历史消息
@room_bp.route("/get_more/anonymous/<int:room_id>")
def get_more_anony(room_id):
    global get_more_page, flag
    get_more_page += 1
    r = AnonymousRoom.query.get(room_id)
    total = AnonymousMessage.query.with_parent(r).count()
    total_pages = math.ceil(total / 8)
    if get_more_page <= total_pages:
        pagination = AnonymousMessage.query.with_parent(r).order_by(AnonymousMessage.timestamp.desc()).paginate(
            get_more_page, 8,
            error_out=True)
        messages = pagination.items
        messages = reversed(messages)
        return jsonify(html=render_template("_anony_more.html", messages=messages), total_pages=total_pages)
    return jsonify(total_pages=total_pages)


# 进入匿名房间前创建虚拟用户
@room_bp.route("/set_info/<int:room_id>", methods=["POST", "GET"])
@login_required
def set_info(room_id):
    if request.method == "POST":
        anony_name = request.form.get("username")
        anony_face = request.form.get("img").split('/')[-1]
        session["anony_name"] = anony_name
        session["anony_face"] = anony_face
        return redirect(url_for("room_bp.anonymous_room", room_id=room_id, permission=1))

    random_id = random.randint(1, 7)
    fake_name = faker.user_name()
    return render_template("set_info.html", random_id=str(random_id), room_id=room_id, fake_name=fake_name)


@room_bp.route("/change_avatars")
def change_avatars():
    random_id = random.randint(1, 7)
    return url_for('static', filename='user_faces/' + str(random_id) + '.jpg', _external=True)


@room_bp.route("/change_name")
def change_name():
    return faker.user_name()


@room_bp.route('/edit_room/<int:room_id>', methods=["POST", "GET"])
@login_required
def edit_room(room_id):
    r = Room.query.get_or_404(room_id) if request.args.get("anony") == '0' else AnonymousRoom.query.get_or_404(room_id)
    form = EditForm()
    if form.validate_on_submit():
        r.name = form.name.data
        r.info = form.info.data
        f = form.face.data
        if f:
            if r.face != "default":
                os.remove(os.path.join(ROOM_FACE_UPLOAD_PATH, r.face))
            filename = random_filename(f.filename)
            r.face = filename
            f.save(os.path.join(ROOM_FACE_UPLOAD_PATH, filename))
        db.session.commit()
        flash("保存成功!")
        return redirect_back()
    form.name.data = r.name
    form.info.data = r.info
    return render_template("edit_room.html", form=form, r=r)


@room_bp.route("/chat_records/<int:room_id>", methods=["POST", "GET"])
@login_required
def chat_records(room_id):
    anony = request.args.get("anony",0,type = int)
    r = Room.query.get_or_404(room_id) if anony == 0 else AnonymousRoom.query.get_or_404(room_id)
    form = RecordsSearchForm()
    page = request.args.get('page', 1, type=int)
    key = None
    if form.validate_on_submit():
        key = form.key.data
        if anony == 1:
            pagination = AnonymousMessage.query.with_parent(r).whooshee_search(key).order_by(
                AnonymousMessage.timestamp.desc()).paginate(page, 10)
        else:
            pagination = Message.query.with_parent(r).whooshee_search(key).order_by(Message.timestamp.desc()).paginate(
                page,
                10)
    if request.method == "GET":
        if anony == 1:
            pagination = AnonymousMessage.query.with_parent(r).order_by(AnonymousMessage.timestamp.desc()).paginate(
                page, 10)
        else:
            pagination = Message.query.with_parent(r).order_by(Message.timestamp.desc()).paginate(page, 10)
    messages = pagination.items
    return render_template("chat_records.html", pagination=pagination, messages=messages, form=form, key=key, r=r,
                           anony=anony)


@room_bp.route('/delete_room/<int:room_id>', methods=["POST"])
@login_required
def delete_room(room_id):
    filter = request.args.get("filter")
    if filter == "normal":
        r = Room.query.get_or_404(room_id)
    else:
        r = AnonymousRoom.query.get_or_404(room_id)
    try:
        db.session.delete(r)
        db.session.commit()
        flash("删除成功!")
    except Exception as e:
        db.session.rollback()
        print(e)
    finally:
        return redirect_back()

