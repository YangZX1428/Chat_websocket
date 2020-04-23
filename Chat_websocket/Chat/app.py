
from flask import Flask, session
import os
from flask_socketio import SocketIO
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_avatars import Avatars
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_cors import CORS
from .blueprint import db,faker,whooshee
app = Flask(__name__)
DATABASE = "chat"
FACE_UPLOAD_PATH = r"G:\ThirdWork\Chat\static\user_faces"
ROOM_FACE_UPLOAD_PATH = r"G:\ThirdWork\Chat\static\room_faces"


class Config():
    SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI") + DATABASE
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WHOOSHEE_MIN_STRING_LEN = 1
    MAX_CONTENT_FILES = 30
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024

# 注册四个蓝图
app.config.from_object(Config)
from Chat.room import room_bp
app.register_blueprint(room_bp)
from Chat.user import user_bp
app.register_blueprint(user_bp)
from Chat.auth import auth
app.register_blueprint(auth)
from Chat.chat_content import main
app.register_blueprint(main)
# 初始化一些扩展对象
db.init_app(app)
whooshee.init_app(app)
socketio = SocketIO(app)
moment = Moment(app)
bootstrap = Bootstrap(app)
avatars = Avatars(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)
login_manager.login_view = "auth.login"
login_manager.login_message = "您必须先登录"
CORS(app)




@login_manager.user_loader
def load_user(user_id):
    from Chat.models import User
    user = User.query.get(int(user_id))
    return user

# 全局常量为房间总数
@app.context_processor
def Const_val():
    from Chat.models import Room
    total_room = Room.query.count()
    return dict(total_room=total_room)

# 初始化虚拟用户名和头像
@app.before_first_request
def init():
    session["anony_name"] = None
    session["anony_face"] = None