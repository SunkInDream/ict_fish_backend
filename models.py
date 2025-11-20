# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class TimestampMixin:
    """时间戳混入：给表加 created_at / updated_at 字段"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class User(TimestampMixin, db.Model):
    """用户表：对应个人中心"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 登录账号（邮箱或用户名）
    account = db.Column(db.String(100), unique=True, nullable=False)

    # 昵称 / 姓名
    name = db.Column(db.String(50), nullable=False)

    # 密码哈希（不保存明文密码）
    password_hash = db.Column(db.String(200), nullable=False)

    # 头像
    avatar_url = db.Column(db.String(255), nullable=True)

    # 手机号
    phone = db.Column(db.String(20), nullable=True)

    # 性别：男 / 女 / 未知
    gender = db.Column(db.String(10), nullable=True)

    # 生日
    birthday = db.Column(db.Date, nullable=True)

    # 地区
    region = db.Column(db.String(100), nullable=True)

    # 关系
    comments = db.relationship("Comment", backref="user", lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Comment(TimestampMixin, db.Model):
    """评论表"""
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )

    content = db.Column(db.Text, nullable=False)

    # 状态：pending（待审核）/ approved（通过）/ rejected（拒绝）
    status = db.Column(db.String(20), default="pending", nullable=False)


class RepairRequest(TimestampMixin, db.Model):
    """报修表"""
    __tablename__ = "repair_requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # 状态：pending / processing / done / canceled
    status = db.Column(db.String(20), default="pending", nullable=False)


class ActivityLog(TimestampMixin, db.Model):
    """活动记录表"""
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )

    # 活动类型，如 login / comment / repair_submit 等
    action = db.Column(db.String(50), nullable=False)
    # 额外信息（JSON 字符串）
    detail = db.Column(db.Text, nullable=True)
