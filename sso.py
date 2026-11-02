from urllib.parse import unquote

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pengaturan import SECRET_KEY

COOKIE = "smartmu_sso"
UMUR = 60 * 60 * 12
_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="smartmu-sso")


def buat(data):
    return _serializer.dumps(data)


def _muat(token):
    if not token:
        return None
    try:
        data = _serializer.loads(unquote(token), max_age=UMUR)
    except (BadSignature, SignatureExpired):
        return None
    if not isinstance(data, dict) or not data.get("username"):
        return None
    return data


def baca(request):
    return _muat(request.cookies.get(COOKIE, ""))


def baca_cookie(header):
    if not header:
        return None
    for bagian in header.split(";"):
        if "=" not in bagian:
            continue
        kunci, nilai = bagian.strip().split("=", 1)
        if kunci == COOKIE:
            return _muat(nilai)
    return None


def boleh_data(data, portal):
    if not data or not data.get("username"):
        return False
    if data.get("role") == "admin":
        return True
    if data.get("role") == "orang_tua":
        return portal == "tahfidz"
    from portal.akun import akses_username

    return portal in akses_username(data.get("username") or "")


def cegah_ubah(request, pengecualian=()):
    """Pengguna portal selain admin hanya membuka portal, tidak mengubah data."""
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return None
    data = baca(request)
    if not data or data.get("role") in {"admin", "orang_tua"}:
        return None
    if request.endpoint in pengecualian:
        return None
    if request.path.startswith("/api/"):
        from flask import jsonify

        return jsonify(error="Perubahan data hanya dapat dilakukan admin."), 403
    from flask import make_response

    halaman = """<!DOCTYPE html>
<html lang="id"><meta charset="utf-8"><title>Hanya admin</title>
<body style="font-family:Segoe UI,sans-serif;padding:32px">
<p>Akun ini hanya dapat membuka portal. Perubahan data hanya dapat dilakukan admin.</p>
<p><a href="/">Kembali ke beranda</a></p>
</body></html>"""
    return make_response(halaman, 403)


def pasang(response, data):
    response.set_cookie(
        COOKIE,
        buat(data),
        max_age=UMUR,
        httponly=True,
        samesite="Lax",
        path="/",
    )
    return response


def hapus(response):
    response.delete_cookie(COOKIE, path="/")
    return response
