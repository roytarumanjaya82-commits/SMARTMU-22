from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from tpk.utils import redirect_by_role

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)
    return render_template("index.html")


@main_bp.app_errorhandler(403)
def forbidden(_error):
    return render_template("errors/403.html"), 403


@main_bp.app_errorhandler(404)
def not_found(_error):
    return render_template("errors/404.html"), 404