from flask import Blueprint, render_template, request
from flask_login import login_required

from app import models

pengembalian_bp = Blueprint("pengembalian", __name__, url_prefix="/pengembalian")


@pengembalian_bp.route("/")
@login_required
def index():
    q = (request.args.get("q") or "").strip().lower()
    items = models.list_peminjaman(status="Dipinjam")
    if q:
        items = [
            p for p in items
            if q in (p.get("peminjam") or "").lower()
            or q in (p.get("barang_nama") or "").lower()
            or q in (p.get("barang_kode") or "").lower()
            or q in (p.get("kelas_unit") or "").lower()
        ]
    return render_template("pengembalian/index.html", items=items, q=request.args.get("q") or "")
