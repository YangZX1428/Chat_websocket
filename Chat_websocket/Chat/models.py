from Chat.app import db, whooshee,faker
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
"""
定义了四个表，分别保存普通房间及消息记录，匿名房间及消息记录
"""
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    face = db.Column(db.String(60), default="default")
    info = db.Column(db.Text)
    messages = db.relationship("Message", back_populates="author", cascade="all")
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"))
    room = db.relationship("Room", back_populates="users")
    created_room_id = db.Column(db.String(20))
    is_login = db.Column(db.Boolean,default=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_pwd(self, password):
        return check_password_hash(self.password_hash, password)

@whooshee.register_model("body")
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates="messages")
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', back_populates="messages")


@whooshee.register_model('name')
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False, unique=True)
    info = db.Column(db.Text, default='无')
    face = db.Column(db.String(255), default="default")
    users = db.relationship("User", back_populates="room", cascade="all")
    messages = db.relationship("Message", back_populates="room", cascade="all")
    create_user_id = db.Column(db.Integer)
    url = db.Column(db.String(60), nullable=False, unique=True)

@whooshee.register_model("name")
class AnonymousRoom(db.Model):
    __tablename__ = "anony_room"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False, unique=True)
    info = db.Column(db.Text, default='无')
    face = db.Column(db.String(255), default="default")
    messages = db.relationship("AnonymousMessage", back_populates="room", cascade="all")
    create_user_id = db.Column(db.Integer)
    url = db.Column(db.String(60), nullable=False, unique=True)
    online = db.Column(db.Integer,default = 0)

@whooshee.register_model("body")
class AnonymousMessage(db.Model):
    __tablename__ = "anony_messages"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    face = db.Column(db.String(255), default="default")
    author = db.Column(db.String(255),nullable = False)
    room_id = db.Column(db.Integer, db.ForeignKey('anony_room.id'))
    room = db.relationship('AnonymousRoom', back_populates="messages")


