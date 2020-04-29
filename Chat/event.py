from flask import render_template, session
from Chat.app import socketio, db
from flask_login import current_user
from flask_socketio import emit, leave_room, join_room
from Chat.models import User, Message, Room, AnonymousRoom, AnonymousMessage

"""
定义各种事件监听器
包括 加入/退出房间事件，获取房间在线人数，以及发送消息事件
"""


# 处理发送消息
@socketio.on('new message')
def new_message(msg):
    message = msg[0]
    room_id = msg[1]
    author = msg[2]
    u = User.query.filter_by(username=author).first()
    m = Message(body=message, author_id=current_user.id, room_id=room_id)
    r = Room.query.get_or_404(room_id)
    room = r.url
    try:
        if message.strip() is not '':
            db.session.add(m)
            db.session.commit()
        emit('new message',
         {'message_html': render_template("_message.html", content=message, face=u.face,
                                          username=author,m=m),
          "error":0},
         broadcast=True, room=room)
    except Exception as e:
        db.session.rollback()
        print(e)
        emit("new message",{"error":1,"message":"发送失败!"},room=room)



# 处理普通房间加入事件,同时更新在线人数
@socketio.on('join')
def join(room_id):
    r = Room.query.get_or_404(room_id)
    room = r.url
    if current_user._get_current_object() not in r.users:
        r.users.append(current_user._get_current_object())
        db.session.commit()
    count = len(r.users)
    join_room(room)
    emit("status", {"username": current_user.username, "count": count, "type": "join"}, broadcast=True, room=room)


# 处理普通房间离开事件,并更新在线人数
@socketio.on('leave')
def leave(room_id):
    r = Room.query.get_or_404(room_id)
    room = r.url
    if r.users and current_user._get_current_object() in r.users:
        r.users.remove(current_user._get_current_object())
        db.session.commit()
    leave_room(room)
    count = len(r.users)
    emit("status", {"username": current_user.username, "count": count, "type": "leave"}, broadcast=True, room=room)


# 匿名房间消息处理
@socketio.on("new message", namespace="/anonymous")
def anony_message(msg):
    anony_name = session.get("anony_name")
    anony_face = session.get("anony_face")
    message = msg[0]
    room_id = msg[1]
    id = max([mess.id for mess in AnonymousMessage.query.all()]) + 1
    m = AnonymousMessage(id=id, body=message, face=anony_face, author=anony_name, room_id=room_id)
    r = AnonymousRoom.query.get_or_404(room_id)
    room = r.url
    try:
        db.session.add(m)
        db.session.commit()
        emit('new message',
             {'html': render_template("_message.html", content=message, face=anony_face,
                                      username=anony_name, m=m)},
             broadcast=True, namespace="/anonymous", room=room)
    except Exception as e:
        print(e)
        db.session.rollback()
        emit("new message",{"error":1,"message":"发送失败!"},room=room,namespace="/anonymous")




# 匿名房间进入房间,并更新在线人数
@socketio.on("join", namespace="/anonymous")
def join(room_id):
    r = AnonymousRoom.query.get_or_404(room_id)
    room = r.url
    join_room(room, namespace="/anonymous")
    r.online += 1
    db.session.commit()
    count = r.online
    emit("status", {"html": session.get("anony_name") + "进入了聊天室", "count": count, "type": "join"}, broadcast=True,
         room=room, namespace="/anonymous")


# 匿名房间离开房间，并更新在线人数
@socketio.on("leave", namespace="/anonymous")
def leave(room_id):
    r = AnonymousRoom.query.get_or_404(room_id)
    room = r.url
    leave_room(room, namespace="/anonymous")
    if r.online >= 1:
        r.online -= 1
    db.session.commit()
    count = r.online
    emit("status", {"html": session.get("anony_name") + "离开了聊天室", "count": count, "type": "leave"}, broadcast=True,
         room=room, namespace="/anonymous")
