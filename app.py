# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from models import db, User, Comment, TankStatus, DeviceSetting


def create_app():
    app = Flask(__name__)

    # SQLite 数据库文件
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///miniapp.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CORS(app)

    # 初始化数据库（如果表不存在就创建）
    with app.app_context():
        db.create_all()

    @app.route("/ping")
    def ping():
        return jsonify({"msg": "pong"}), 200

    # ====================== 注册 ======================
    @app.route("/api/register", methods=["POST"])
    def register():
        data = request.get_json() or {}

        account = data.get("account")
        password = data.get("password")
        name = data.get("name")
        phone = data.get("phone")
        gender = data.get("gender")
        birthday_str = data.get("birthday")
        region = data.get("region")
        avatar = data.get("avatar")

        if not account or not password or not name:
            return jsonify({"error": "account, password and name are required"}), 400

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

        return jsonify({"id": user.id, "name": user.name}), 201

    # ====================== 登录 ======================
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

        return jsonify({"id": user.id, "name": user.name}), 200

    # ====================== 获取用户信息 ======================
    @app.route("/api/users/<int:user_id>", methods=["GET"])
    def get_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "user not found"}), 404

        return jsonify({
            "id": user.id,
            "avatar": user.avatar_url,
            "name": user.name,
            "account": user.account,
            "phone": user.phone,
            "gender": user.gender,
            "birthday": user.birthday.isoformat() if user.birthday else None,
            "region": user.region,
        }), 200

    # ====================== 获取鱼缸最新状态 ======================
    @app.route("/api/tank/status", methods=["GET"])
    def get_tank_status():
        status = TankStatus.query.order_by(TankStatus.created_at.desc()).first()

        if not status:
            # 没有数据时返回默认值
            return jsonify({
                "update_time": None,
                "temp": None,
                "ph": None,
                "tds": None,
                "temp_status": "normal",
                "ph_status": "normal",
                "tds_status": "normal",
            }), 200

        return jsonify({
            "update_time": status.created_at.isoformat(),
            "temp": status.temp,
            "ph": status.ph,
            "tds": status.tds,
            "temp_status": status.temp_status,
            "ph_status": status.ph_status,
            "tds_status": status.tds_status,
        }), 200

    # ====================== 写入一条鱼缸状态 ======================
    @app.route("/api/tank/status", methods=["POST"])
    def create_tank_status():
        data = request.get_json() or {}

        temp = data.get("temp")
        ph = data.get("ph")
        tds = data.get("tds")
        device_id = data.get("device_id")

        def judge_temp(v):
            if v is None:
                return "normal"
            return "abnormal" if v < 5 or v > 40 else "normal"

        def judge_ph(v):
            if v is None:
                return "normal"
            return "abnormal" if v < 6.5 or v > 8.5 else "normal"

        def judge_tds(v):
            if v is None:
                return "normal"
            return "abnormal" if v < 0 or v > 1000 else "normal"

        status = TankStatus(
            device_id=device_id,
            temp=temp,
            ph=ph,
            tds=tds,
            temp_status=judge_temp(temp),
            ph_status=judge_ph(ph),
            tds_status=judge_tds(tds),
        )

        db.session.add(status)
        db.session.commit()

        return jsonify({"msg": "created"}), 201

    # ====================== 记录设备设置 ======================
    @app.route("/api/tank/settings", methods=["POST"])
    def create_setting():
        data = request.get_json() or {}

        setting_name = data.get("setting_name")
        setting_type = data.get("setting_type")
        value = data.get("value")
        user_id = data.get("user_id")

        if not setting_name or not setting_type or value is None:
            return jsonify({"error": "setting_name, setting_type and value are required"}), 400

        record = DeviceSetting(
            user_id=user_id,
            setting_name=setting_name,
            setting_type=setting_type,
            value=str(value),
        )

        db.session.add(record)
        db.session.commit()

        return jsonify({"msg": "setting saved"}), 201

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
