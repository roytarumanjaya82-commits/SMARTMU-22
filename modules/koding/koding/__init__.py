from pathlib import Path

from flask import Flask, redirect, request, session

from koding.config import Config
from koding.db import close_db, query

FOLDER = Path(__file__).resolve().parent


def create_app():
    app = Flask(
        __name__,
        template_folder=str(FOLDER / "templates"),
        static_folder=str(FOLDER / "static"),
    )
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["SESSION_COOKIE_NAME"] = "smartmu_koding"
    app.config["SESSION_COOKIE_PATH"] = "/koding"
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH
    Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    (Config.UPLOAD_FOLDER / "materi").mkdir(parents=True, exist_ok=True)
    Config.BLANKO_FOLDER.mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(close_db)

    from koding.routes.auth import bp as auth_bp
    from koding.routes.admin import bp as admin_bp
    from koding.routes.siswa import bp as siswa_bp
    from koding.routes.penilaian import bp as penilaian_bp
    from koding.routes.public import bp as public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(siswa_bp, url_prefix="/siswa")
    app.register_blueprint(penilaian_bp, url_prefix="/penilaian")

    @app.before_request
    def masuk_dari_portal():
        try:
            from sso import baca, boleh_data, cegah_ubah

            data = baca(request)
        except Exception:
            return None
        if data and not boleh_data(data, "koding"):
            if session.get("dari_portal"):
                session.clear()
            if request.endpoint not in {None, "static", "auth.login"}:
                return redirect("/?akses=koding")
            return None
        if data:
            tertahan = cegah_ubah(request, {"auth.login", "auth.logout"})
            if tertahan is not None:
                return tertahan
        if request.endpoint in {None, "static", "auth.login"} or not data:
            return None
        if session.get("user_id"):
            return None
        guru = query(
            "SELECT * FROM users WHERE role='guru' AND aktif=1 ORDER BY id LIMIT 1",
            one=True,
        )
        if not guru:
            return None
        session.clear()
        session["user_id"] = guru["id"]
        session["username"] = guru["username"]
        session["nama_lengkap"] = data.get("nama") or guru["nama_lengkap"]
        session["role"] = "guru"
        session["dari_portal"] = True
        return None

    @app.context_processor
    def inject_globals():
        from koding.auth_utils import current_user
        from koding.config import JENIS_UJIAN

        return {"current_user": current_user(), "JENIS_UJIAN": JENIS_UJIAN}

    return app
