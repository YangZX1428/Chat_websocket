from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, TextAreaField, HiddenField, PasswordField,SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, URL, EqualTo,Optional


class SearchForm(FlaskForm):
    url = StringField("", validators=[DataRequired(), Length(20, 50,message="url长度必须大于20个字符小于50个字符！"), URL(message="请输入合法的url!")])
    submit = SubmitField("加入")


class CreateForm(FlaskForm):
    room_type = SelectField("请选择房间类型",coerce=int,default=1)
    name = StringField("请输入房间名", validators=[DataRequired(), Length(1, 20)])
    info = TextAreaField("请输入房间简介")
    face = FileField("请上传房间头像", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("创建")
    def __init__(self):
        super(CreateForm, self).__init__()
        self.room_type.choices = [(1,"普通房间"),(2,"匿名房间")]


class RegistForm(FlaskForm):
    name = StringField(label="请输入用户名", validators=[DataRequired("用户名不能为空!")])
    password1 = PasswordField(label="请输入密码", validators=[DataRequired("密码不能为空!")])
    password2 = PasswordField(label="确认密码", validators=[EqualTo("password1", "两次密码不一致!")])
    submit = SubmitField(label="注册")


class LoginForm(FlaskForm):
    name = StringField(label="请输入用户名", validators=[DataRequired("用户名不能为空!")])
    password = PasswordField(label="请输入密码", validators=[DataRequired("密码不能为空!")])
    submit = SubmitField(label="登录")

class SearchRoomForm(FlaskForm):
    name = StringField("", validators=[DataRequired(), Length(1, 20, message="房间名必须大于1个字符小于20个字符！")])
    submit = SubmitField("查询")


class UserInfoForm(FlaskForm):
    username = StringField("用户名",validators=[DataRequired("用户名不能为空!")])
    info = TextAreaField("简介",validators=[Optional()])
    face = FileField("头像(支持上传.jpg,.png文件,且文件大小小于3MB)",validators=[FileAllowed(['jpg','png'],message="仅支持上传jpg,png图片!")])
    submit = SubmitField("保存")


class EditForm(FlaskForm):
    name = StringField("房间名", validators=[DataRequired("房间名不能为空"), Length(1, 20)])
    info = TextAreaField("房间简介")
    face = FileField("房间头像", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("保存")


class RecordsSearchForm(FlaskForm):
    key = StringField("", validators=[DataRequired("搜索内容不得为空!")])
    submit = SubmitField("查询")
