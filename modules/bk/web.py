import json

import pymysql
from flask import Flask, abort, jsonify, request, send_from_directory

from pengaturan import (
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    SECRET_KEY,
    SMARTMU_DATABASE,
)
from portal import tautan_masuk
from sso import baca, boleh_data

import os

FOLDER = os.path.dirname(os.path.abspath(__file__))


def _koneksi():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=SMARTMU_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SESSION_COOKIE_NAME"] = "smartmu_bk"
    app.config["SESSION_COOKIE_PATH"] = "/bk"

    @app.before_request
    def wajib_masuk():
        if request.endpoint == "berkas":
            return None
        data = baca(request)
        if data and not boleh_data(data, "bk"):
            if request.path.startswith("/api/"):
                return jsonify(error="Akun ini tidak dapat membuka Rapor BK."), 403
            return __import__("flask").redirect("/?akses=bk")
        if data and data.get("role") != "admin" and request.method not in {"GET", "HEAD", "OPTIONS"}:
            boleh_tulis = data.get("role") == "guru_bk"
            if data.get("role") == "guru_piket":
                from portal.guru_akun import mengajar_bk

                boleh_tulis = mengajar_bk(data.get("id"))
            if not boleh_tulis:
                if request.path.startswith("/api/"):
                    return jsonify(error="Perubahan data hanya dapat dilakukan admin."), 403
                from sso import cegah_ubah
                return cegah_ubah(request)
        if data:
            return None
        if request.path.startswith("/api/"):
            return jsonify(error="Silakan masuk lewat portal SMARTMU."), 401
        return __import__("flask").redirect(tautan_masuk(request))

    @app.route("/")
    def halaman():
        return send_from_directory(FOLDER, "index.html")

    @app.route("/<path:filename>")
    def berkas(filename):
        if filename.endswith((".py", ".pyc")) or filename.startswith("."):
            abort(404)
        return send_from_directory(FOLDER, filename)

    @app.route("/api/state", methods=["GET", "PUT"])
    def state():
        try:
            conn = _koneksi()
        except pymysql.MySQLError:
            return jsonify(error="Database SMARTMU belum siap."), 503
        try:
            with conn.cursor() as cur:
                if request.method == "GET":
                    cur.execute("SELECT isi FROM bk_dokumen WHERE id=1")
                    row = cur.fetchone()
                    if not row or not row.get("isi"):
                        return jsonify({})
                    return app.response_class(row["isi"], mimetype="application/json")
                mentah = request.get_data(as_text=True) or "{}"
                try:
                    json.loads(mentah)
                except json.JSONDecodeError:
                    return jsonify(error="Data rapor bukan JSON."), 400
                cur.execute(
                    """INSERT INTO bk_dokumen (id, isi) VALUES (1, %s)
                       ON DUPLICATE KEY UPDATE isi=VALUES(isi)""",
                    (mentah,),
                )
            return jsonify(ok=True)
        finally:
            conn.close()

    return app
