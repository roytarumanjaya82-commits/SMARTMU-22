from flask import Flask, request
from flask_login import LoginManager, current_user, login_user

from config import SECRET_KEY, SCHOOL_NAME, SCHOOL_SHORT, RESOURCE_DIR


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Silakan masuk terlebih dahulu."
login_manager.login_message_category = "warning"


def _kunci_sesi(bawaan):
    try:
        from pengaturan import SECRET_KEY as kunci_portal

        return kunci_portal or bawaan
    except Exception:
        return bawaan


def create_app():
    template_folder = str(RESOURCE_DIR / "app" / "templates")
    static_folder = str(RESOURCE_DIR / "app" / "static")

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
    )
    app.config["SECRET_KEY"] = _kunci_sesi(SECRET_KEY)
    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB upload Excel
    app.config["SESSION_COOKIE_NAME"] = "smartmu_inventaris"
    app.config["SESSION_COOKIE_PATH"] = "/inventaris"
    app.config["REMEMBER_COOKIE_PATH"] = "/inventaris"

    login_manager.init_app(app)

    from app.db import init_db
    from app.models import User
    from app.services import google_drive as gdrive

    init_db()

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))

    @app.before_request
    def masuk_dari_portal():
        if request.endpoint in {None, "static", "auth.login"}:
            return None
        if current_user.is_authenticated:
            return None
        try:
            from sso import baca

            data = baca(request)
        except Exception:
            return None
        if not data:
            return None
        user = User.get_by_username(data.get("username") or "")
        if user is None and data.get("role") == "admin":
            from app.db import get_connection

            conn = get_connection()
            try:
                row = conn.execute(
                    "SELECT * FROM users WHERE role=%s ORDER BY id LIMIT 1",
                    ("admin",),
                ).fetchone()
            finally:
                conn.close()
            user = User(row) if row else None
        if user is not None:
            login_user(user)
        return None

    @app.context_processor
    def inject_globals():
        return {
            "school_name": SCHOOL_NAME,
            "school_short": SCHOOL_SHORT,
            "drive_connected": gdrive.is_connected(),
            "drive_offline": gdrive.is_offline(),
        }

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.barang import barang_bp
    from app.routes.peminjaman import peminjaman_bp
    from app.routes.pengembalian import pengembalian_bp
    from app.routes.sync import sync_bp
    from app.routes.laporan import laporan_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(barang_bp)
    app.register_blueprint(peminjaman_bp)
    app.register_blueprint(pengembalian_bp)
    app.register_blueprint(sync_bp)
    app.register_blueprint(laporan_bp)
    app.register_blueprint(users_bp)

    return app
