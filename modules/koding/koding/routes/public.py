from flask import Blueprint, redirect, url_for, session

bp = Blueprint("public", __name__)


@bp.route("/")
def index():
    if "user_id" in session:
        if session.get("role") == "guru":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("siswa.dashboard"))
    return redirect(url_for("auth.login"))
