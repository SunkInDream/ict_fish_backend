# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from models import db, User, Comment


def create_app():
    app = Flask(__name__)

    # SQLite 数据库文件
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///miniapp.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CORS(app)

    # 初始化数据库
    with app.app_context():
        db.create_all()

    @app.route("/ping")
    def ping():
        return jsonify({"msg": "pong"}), 200

    # 注册接口：POST /api/register
    # 请求体：{"account": "...", "password": "...", "name": "...", 其他可选字段}
    @app.route("/api/register", methods=["POST"])
    def register():
        data = request.get_json() or {}

        account = data.get("account")
        password = data.get("password")
        name = data.get("name")

        phone = data.get("phone")
        gender = data.get("gender")
        birthday_str = data.get("birthday")  # 预期格式：YYYY-MM-DD
        region = data.get("region")
        avatar = data.get("avatar")

        if not account or not password or not name:
            return jsonify({"error": "account, password and name are required"}), 400

        # 账号是否已存在
        if User.query.filter_by(account=account).first():
            return jsonify({"error": "account already exists"}), 409

        birthday = None
        if birthday_str:
            try:
                birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "birthday format must be YYYY-MM-DD"}), 400

        user = User(
            account=account,
            name=name,
            phone=phone,
            gender=gender,
            birthday=birthday,
            region=region,
            avatar_url=avatar,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return jsonify(
            {
                "id": user.id,
                "name": user.name,
            }
        ), 201

    # 登录接口：POST /api/login
    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        account = data.get("account")
        password = data.get("password")

        if not account or not password:
            return jsonify({"error": "account and password are required"}), 400

        user = User.query.filter_by(account=account).first()
        if not user:
            return jsonify({"error": "user not found"}), 404

        if not user.check_password(password):
            return jsonify({"error": "wrong password"}), 401

        return jsonify(
            {
                "id": user.id,
                "name": user.name,
            }
        ), 200

    # 获取用户信息：GET /api/users/<id>
    @app.route("/api/users/<int:user_id>", methods=["GET"])
    def get_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "user not found"}), 404

        data = {
            "id": user.id,
            "avatar": user.avatar_url,
            "name": user.name,
            "account": user.account,
            "phone": user.phone,
            "gender": user.gender,
            "birthday": user.birthday.isoformat() if user.birthday else None,
            "region": user.region,
        }
        return jsonify(data), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
