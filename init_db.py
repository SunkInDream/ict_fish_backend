from datetime import date
from app import create_app
from models import db, User, Comment

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    user = User(
        account="tang_biao@qq.com",
        name="唐彪",
        avatar_url="/static/avatar/default.png",
        phone="18200008719",
        gender="男",
        birthday=date(2004, 11, 30),
        region="中国",
    )
    user.set_password("123456")  # ⭐ 密码 123456

    db.session.add(user)
    db.session.commit()

    c1 = Comment(
        user_id=user.id,
        content="这个鱼缸真不错！",
        status="approved",
    )
    c2 = Comment(
        user_id=user.id,
        content="水质有点问题，需要检查过滤器。",
        status="pending",
    )
    db.session.add_all([c1, c2])
    db.session.commit()

    print("✅ 数据库初始化完成：创建了 1 个用户和 2 条评论")
    print(f"用户 ID: {user.id}, 账号: {user.account}, 密码: 123456")
