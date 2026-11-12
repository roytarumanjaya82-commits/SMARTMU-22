from functools import wraps
from flask import session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from koding import db


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def login_user(user: dict):
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["nama_lengkap"] = user["nama_lengkap"]
    session["role"] = user["role"]
    if user["role"] == "siswa":
        siswa = db.query(
            """
            SELECT s.id, s.kelas_id, s.nis, k.nama_kelas, k.tingkat
            FROM siswa s
            LEFT JOIN kelas k ON k.id=s.kelas_id
            WHERE s.user_id=%s
            """,
            (user["id"],),
            one=True,
        )
        if siswa:
            from koding.tingkat_utils import tingkat_dari_nama_kelas

            session["siswa_id"] = siswa["id"]
            session["kelas_id"] = siswa["kelas_id"]
            session["nis"] = siswa["nis"]
            session["nama_kelas"] = siswa.get("nama_kelas")
            session["tingkat"] = siswa.get("tingkat") or tingkat_dari_nama_kelas(
                siswa.get("nama_kelas")
            )


def logout_user():
    session.clear()


def current_user():
    if "user_id" not in session:
        return None
    return {
        "id": session["user_id"],
        "username": session.get("username"),
        "nama_lengkap": session.get("nama_lengkap"),
        "role": session.get("role"),
        "siswa_id": session.get("siswa_id"),
        "kelas_id": session.get("kelas_id"),
        "nis": session.get("nis"),
        "nama_kelas": session.get("nama_kelas"),
        "tingkat": session.get("tingkat", "7"),
    }


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def guru_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if session.get("role") != "guru":
            flash("Akses khusus guru/admin.", "danger")
            return redirect(url_for("siswa.dashboard"))
        return view(*args, **kwargs)

    return wrapped


def siswa_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if session.get("role") != "siswa":
            flash("Menu ini untuk siswa.", "danger")
            return redirect(url_for("admin.dashboard"))
        return view(*args, **kwargs)

    return wrapped
