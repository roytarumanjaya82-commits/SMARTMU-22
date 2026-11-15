from flask import Flask, redirect, request, session
from flask_login import current_user, login_user

from tpk.extensions import db, login_manager
from tpk.settings import Config


def _pastikan_database(config_class=Config):
    import pymysql

    conn = pymysql.connect(
        host=config_class.MYSQL_HOST,
        port=int(config_class.MYSQL_PORT),
        user=config_class.MYSQL_USER,
        password=config_class.MYSQL_PASSWORD or "",
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{config_class.MYSQL_DATABASE}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        conn.close()


def create_app(config_class=Config):
    _pastikan_database(config_class)
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["SESSION_COOKIE_NAME"] = "smartmu_tpk"
    app.config["SESSION_COOKIE_PATH"] = "/tpk"
    app.config["REMEMBER_COOKIE_PATH"] = "/tpk"

    db.init_app(app)
    login_manager.init_app(app)

    from tpk.auth.routes import auth_bp
    from tpk.admin.routes import admin_bp
    from tpk.guru.routes import guru_bp
    from tpk.guru_soal.routes import guru_soal_bp
    from tpk.murid.routes import murid_bp
    from tpk.ortu.routes import ortu_bp
    from tpk.main.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(guru_bp, url_prefix="/guru")
    app.register_blueprint(guru_soal_bp, url_prefix="/guru-soal")
    app.register_blueprint(murid_bp, url_prefix="/murid")
    app.register_blueprint(ortu_bp, url_prefix="/ortu")

    @app.before_request
    def masuk_dari_portal():
        try:
            from sso import baca, boleh_data, cegah_ubah

            data = baca(request)
        except Exception:  # noqa: BLE001
            data = None
            cegah_ubah = None

        if data and not boleh_data(data, "tpk"):
            if session.get("dari_portal"):
                from flask_login import logout_user

                logout_user()
                session.pop("dari_portal", None)
            if request.endpoint not in {None, "static", "auth.login", "main.index"}:
                return redirect("/?akses=tpk")
            return None

        if cegah_ubah is not None and session.get("dari_portal"):
            tertahan = cegah_ubah(request, {"auth.login", "main.index"})
            if tertahan is not None:
                return tertahan

        if request.endpoint in {None, "static", "auth.login", "main.index"} or not data:
            return None
        if current_user.is_authenticated:
            return None

        from tpk.models import User

        username = (data.get("username") or "").strip().lower()
        user = User.query.filter_by(username=username).first() if username else None
        if user is None and data.get("role") == "admin":
            user = User.query.filter_by(role="admin", is_active_user=True).order_by(User.id).first()
        if user is not None and user.is_active_user:
            login_user(user)
            session["dari_portal"] = True
        return None

    @app.context_processor
    def inject_sekolah_context():
        from tpk.utils import (
            get_daftar_gelombang,
            get_gelombang_aktif,
            get_tahun_ajaran,
            label_gelombang,
        )

        try:
            return {
                "tahun_ajaran": get_tahun_ajaran(),
                "gelombang_aktif": get_gelombang_aktif(),
                "daftar_gelombang": get_daftar_gelombang(),
                "label_gelombang": label_gelombang,
                "lock_mode": False,
            }
        except Exception:  # noqa: BLE001
            return {
                "tahun_ajaran": "2026/2027",
                "gelombang_aktif": "1",
                "daftar_gelombang": ["1", "2", "3"],
                "label_gelombang": lambda v: f"Gelombang {v}" if v else "-",
                "lock_mode": False,
            }

    with app.app_context():
        from tpk.schema_sync import sync_schema
        from tpk.seed import seed_initial_data

        sync_schema()
        seed_initial_data()

    return app
