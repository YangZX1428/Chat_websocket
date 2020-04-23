from flask import Blueprint, render_template, flash, redirect, url_for, request,session
from flask_login import current_user, login_required
from Chat.app import ROOM_FACE_UPLOAD_PATH,FACE_UPLOAD_PATH
from Chat.models import User, Room, AnonymousRoom
from Chat.forms import CreateForm, SearchRoomForm, UserInfoForm
import os
from flask_dropzone import random_filename
"""
定义了有关用户的视图
包括创建房间，查看房间，查看我创建的房间 以及 用户个人主页
"""
user_bp = Blueprint("user_bp", __name__)


@user_bp.route('/create_room', methods=["POST", "GET"])
@login_required
def create_room():
    from Chat.app import db
    form = CreateForm()
    user_id = current_user.id
    if form.validate_on_submit():
        name = form.name.data
        info = form.info.data
        f = form.face.data
        filename = "default"
        if f:
            filename = random_filename(f.filename)
            f.save(os.path.join(ROOM_FACE_UPLOAD_PATH, filename))
        if form.room_type.data == 1:
            room_id = 1
            if Room.query.all():
                room_id = max([r.id for r in Room.query.all()]) + 1
            r = Room(id=room_id, name=name, info=info, face=filename, create_user_id=user_id,
                     url=url_for("room_bp.chat_page", room_id=room_id, _external=True))
        else:
            room_id = 1
            if AnonymousRoom.query.all():
                room_id = max([r.id for r in AnonymousRoom.query.all()]) + 1
            r = AnonymousRoom(id=room_id, name=name, info=info, face=filename, create_user_id=user_id,
                              url=url_for("room_bp.anonymous_room", room_id=room_id, _external=True))
        db.session.add(r)
        db.session.commit()
        return redirect(url_for('room_bp.chat_page', room_id=room_id, create=1))
    return render_template("create.html", form=form)


@user_bp.route('/check_room', methods=["POST", "GET"])
@login_required
def check_room():
    filter = request.args.get("filter", "normal")
    form = SearchRoomForm()
    page = request.args.get('page', 1, type=int)
    if not request.form.get("name"):
        if filter == "normal":
            pagination = Room.query.order_by(Room.id).paginate(page, 8)
        else:
            pagination = AnonymousRoom.query.order_by(AnonymousRoom.id).paginate(page, 8)
    else:
        key = request.form.get("name")
        if filter == "normal":
            pagination = Room.query.whooshee_search(key).order_by(Room.id.asc()).paginate(page, 8)
        else:
            pagination = AnonymousRoom.query.whooshee_search(key).order_by(AnonymousRoom.id.asc()).paginate(page, 8)
    rooms = pagination.items
    create_user = [User.query.get(r.create_user_id) for r in rooms]
    online_list = [r.online for r in AnonymousRoom.query.all()]
    return render_template("check_room.html", pagination=pagination, rooms=rooms, form=form, create_user=create_user,online_list = online_list)


@user_bp.route("/user_page/<int:user_id>", methods=["POST", "GET"])
@login_required
def user_page(user_id):
    from Chat.app import db
    u = User.query.get(user_id)
    form = UserInfoForm()
    if form.validate_on_submit():
        username = form.username.data
        u.info = form.info.data
        f = form.face.data
        if username != u.username and User.query.filter_by(username=username).first():
            flash("该用户名已被使用！")
            return redirect(url_for('user_bp.user_page', user_id=user_id, submit=0))
        u.username = username
        if f:
            if u.face != "default":
                os.remove(os.path.join(FACE_UPLOAD_PATH, u.face))
            file_name = random_filename(f.filename)
            u.face = file_name
            f.save(os.path.join(FACE_UPLOAD_PATH, file_name))
        db.session.commit()
        flash("保存成功!")
        return redirect(url_for('user_bp.user_page', user_id=user_id, submit=1))
    form.username.data = u.username
    if u.info == "None":
        form.info.data = "无简介"
    else:
        form.info.data = u.info
    return render_template("Userpage.html", u=u, form=form)


@user_bp.route('/my_rooms')
@login_required
def my_rooms():
    filter = request.args.get("filter", "normal")
    page = request.args.get('page', 1, type=int)
    if filter == "normal":
        pagination = Room.query.filter_by(create_user_id=current_user.id).order_by(Room.id).paginate(page, 8)
    else:
        pagination = AnonymousRoom.query.filter_by(create_user_id=current_user.id).order_by(AnonymousRoom.id).paginate(page, 8)
    rooms = pagination.items
    online_list = [r.online for r in AnonymousRoom.query.all()]
    return render_template("my_rooms.html", rooms=rooms, pagination=pagination,filter = filter,online_list = online_list)



