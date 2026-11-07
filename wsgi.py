"""SMARTMU 22 — satu aplikasi untuk Presensi, eRapor, Tahfidz, Rapor BK, dan Inventaris."""

import importlib.util
import sys
from pathlib import Path

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from portal import create_app  # noqa: E402
from portal.akun import akses_username  # noqa: E402
from portal.rawat import aktif as rawat_aktif  # noqa: E402
from sso import baca_cookie, boleh_data  # noqa: E402

PORTAL = create_app()


def _muat_berkas(nama, jalur):
    spec = importlib.util.spec_from_file_location(nama, jalur)
    modul = importlib.util.module_from_spec(spec)
    sys.modules[nama] = modul
    spec.loader.exec_module(modul)
    return modul


def _muat_erapor():
    sys.path.insert(0, str(ROOT / "modules" / "erapor"))
    from erapor import create_app as buat

    aplikasi = buat()
    aplikasi.config["SESSION_COOKIE_NAME"] = "smartmu_erapor"
    aplikasi.config["SESSION_COOKIE_PATH"] = "/erapor"
    return aplikasi


def _muat_tahfidz():
    sys.path.insert(0, str(ROOT / "modules" / "tahfidz"))
    modul = _muat_berkas("tahfidz_app", ROOT / "modules" / "tahfidz" / "app.py")
    modul.app.config["SESSION_COOKIE_NAME"] = "smartmu_tahfidz"
    modul.app.config["SESSION_COOKIE_PATH"] = "/tahfidz"
    return modul.app


def _muat_presensi():
    folder = str(ROOT / "modules" / "presensi")
    sys.path.insert(0, folder)
    try:
        modul = _muat_berkas("presensi_app", ROOT / "modules" / "presensi" / "app.py")
        return modul.app
    finally:
        while folder in sys.path:
            sys.path.remove(folder)


def _muat_bk():
    modul = _muat_berkas("bk_web", ROOT / "modules" / "bk" / "web.py")
    return modul.create_app()


def _muat_inventaris():
    from muat_inventaris import muat

    return muat()


def _wajib_garis_miring(aplikasi):
    def wsgi(environ, start_response):
        if environ.get("PATH_INFO", "") == "":
            lokasi = (environ.get("SCRIPT_NAME") or "") + "/"
            pertanyaan = environ.get("QUERY_STRING")
            if pertanyaan:
                lokasi += "?" + pertanyaan
            start_response("302 FOUND", [("Location", lokasi), ("Content-Length", "0")])
            return [b""]
        return aplikasi(environ, start_response)

    return wsgi


_GAYA = """
<style>
#smartmu-switch{position:fixed;top:0;left:0;right:0;z-index:5000;height:44px;max-height:44px;overflow:hidden;display:flex;align-items:stretch;gap:10px;padding:0 12px;background:#0c4f3b;color:#f3efe6;font:600 14px/1 "Segoe UI",sans-serif}
#smartmu-switch a{color:#f3efe6;text-decoration:none;padding:6px 8px;border-radius:8px;white-space:nowrap}
#smartmu-switch a.on,#smartmu-switch a:hover{background:#fff;color:#0c4f3b}
#smartmu-switch nav{display:flex;flex-direction:row;flex-wrap:nowrap;align-items:center;gap:2px;overflow:auto;flex:1;min-width:0;height:44px}
#smartmu-switch .nama{font-weight:800;letter-spacing:-.02em}
#smartmu-garis{display:none;margin-left:auto;width:42px;height:36px;border:0;background:transparent;padding:8px;flex-direction:column;justify-content:center;gap:5px;cursor:pointer}
#smartmu-garis span{display:block;height:2px;border-radius:2px;background:#f3efe6}
body{padding-top:44px !important}
.topbar{top:44px !important}
.sidebar{top:calc(44px + var(--header-h, 0px)) !important;height:calc(100vh - 44px - var(--header-h, 0px)) !important}
#app .app{height:calc(100vh - 44px) !important}
@media (max-width: 760px){
  #smartmu-garis{display:inline-flex}
  #smartmu-switch.buka{overflow:visible}
  #smartmu-switch nav{display:none;position:absolute;top:44px;left:0;right:0;z-index:1;flex:none;flex-direction:column;align-items:stretch;height:auto;gap:4px;max-height:calc(100dvh - 44px);overflow-y:auto;background:#0c4f3b;padding:8px 10px 14px;border-top:1px solid rgba(255,255,255,.16);box-shadow:0 16px 32px rgba(0,0,0,.2)}
  #smartmu-switch.buka nav{display:flex}
  #smartmu-switch nav a{padding:13px 12px}
  html,body{height:auto !important;overflow:auto !important}
  #app,#app .app{height:auto !important;min-height:calc(100vh - 44px)}
}
@media print{#smartmu-switch{display:none !important}body{padding-top:0 !important}.sidebar,.topbar{top:0 !important;height:auto !important}}
</style>
""".encode("utf-8")

_SKRIP = """
<script>
(function () {
  var batang = document.getElementById("smartmu-switch");
  var tombol = document.getElementById("smartmu-garis");
  var menu = batang && batang.querySelector("nav");
  if (!batang || !tombol || !menu) return;
  tombol.addEventListener("click", function () {
    var buka = batang.classList.toggle("buka");
    tombol.setAttribute("aria-expanded", buka ? "true" : "false");
    tombol.setAttribute("aria-label", buka ? "Tutup menu" : "Buka menu");
  });
  menu.addEventListener("click", function (ev) {
    if (ev.target.closest("a")) batang.classList.remove("buka");
  });
})();
</script>
""".encode("utf-8")

_MENU = (
    ("/", "Beranda"),
    ("/presensi/", "Presensi"),
    ("/erapor/", "eRapor"),
    ("/tahfidz/", "Tahfidz"),
    ("/bk/", "Rapor BK"),
    ("/inventaris/", "Inventaris"),
)


_PINTU = (
    ("/presensi", "presensi", ("/login", "/daftar", "/lupa", "/ortu", "/static/", "/sw.js", "/offline")),
    ("/erapor", "erapor", ("/login", "/static/")),
    ("/tahfidz", "tahfidz", ("/login", "/static/")),
    ("/bk", "bk", ()),
    ("/inventaris", "inventaris", ("/login", "/static/")),
)


def _punya_mapel(data):
    if not data or not data.get("id"):
        return False
    if data.get("role") not in {"guru_piket", "guru_bk", "guru_pengampu"}:
        return False
    from portal.guru_akun import punya_mapel

    return punya_mapel(data.get("id"))


def _guru_bk(data):
    if not data:
        return False
    if data.get("role") == "guru_bk" or data.get("bk"):
        return True
    if data.get("role") == "guru_piket":
        from portal.guru_akun import mengajar_bk

        return mengajar_bk(data.get("id"))
    return False


def _jalur_pengampu(sisa):
    if sisa.startswith("/static/"):
        return True
    dasar = sisa.split("?", 1)[0].rstrip("/") or "/"
    return dasar in {"/", "/hasil-belajar", "/ganti-password", "/keluar", "/sw.js", "/offline"}


def _jalur_guru(sisa):
    if sisa.startswith("/static/"):
        return True
    dasar = sisa.split("?", 1)[0].rstrip("/") or "/"
    return dasar in {
        "/",
        "/presensi",
        "/tata-tertib",
        "/laporan-harian",
        "/rekap-bulanan",
        "/hasil-belajar",
        "/ganti-password",
        "/keluar",
        "/sw.js",
        "/offline",
    }


def _jalur_ortu(sisa):
    if sisa in ("", "/") or sisa.startswith("/static/"):
        return True
    return sisa.split("?", 1)[0] in ("/ortu/pengumuman", "/ortu/hasil-belajar", "/ortu/keluar")


def _publik(sisa, daftar):
    for awalan in daftar:
        if sisa == awalan or sisa.startswith(awalan):
            return True
    return False


def _tolak_portal(environ):
    path = environ.get("PATH_INFO") or "/"
    data = baca_cookie(environ.get("HTTP_COOKIE", ""))
    if not data:
        return None
    for awalan, kunci, publik in _PINTU:
        if path != awalan and not path.startswith(awalan + "/"):
            continue
        sisa = path[len(awalan) :] or "/"
        if _publik(sisa, publik):
            return None
        if data.get("role") == "orang_tua":
            if kunci == "tahfidz":
                from portal.kelas_ortu import anak_ikut_tahfidz

                if anak_ikut_tahfidz(data.get("username"), data.get("id")):
                    return None
                dasar = sisa.split("?", 1)[0]
                if dasar in ("/logout", "/ganti-password") or dasar.startswith("/ganti-password/"):
                    return None
                return "/presensi/ortu/pengumuman"
            if kunci == "presensi" and _jalur_ortu(sisa):
                return None
            return "/?akses=" + kunci
        if data.get("role") == "guru_pengampu":
            if kunci == "presensi" and _jalur_pengampu(sisa):
                return None
            return "/presensi/hasil-belajar"
        if data.get("role") == "guru_bk":
            if kunci == "bk":
                return None
            if kunci == "presensi" and _jalur_pengampu(sisa):
                return None
            return "/bk/"
        if data.get("role") == "guru_piket":
            if kunci == "bk" and _guru_bk(data):
                return None
            if kunci != "presensi" or not _jalur_guru(sisa):
                return "/presensi/presensi"
            return None
        if not boleh_data(data, kunci):
            return "/?akses=" + kunci
    return None


def _menu_untuk(environ):
    data = baca_cookie(environ.get("HTTP_COOKIE", ""))
    if not data:
        return (("/", "Beranda"),)
    if data.get("role") == "admin":
        return _MENU
    if data.get("role") == "orang_tua":
        from portal.kelas_ortu import anak_ikut_tahfidz

        umum = (
            ("/presensi/ortu/pengumuman", "Pengumuman"),
            ("/presensi/ortu/hasil-belajar", "Hasil Belajar"),
            ("/tahfidz/ganti-password", "Ganti Password"),
        )
        if anak_ikut_tahfidz(data.get("username"), data.get("id")):
            return (
                ("/tahfidz/", "Laporan Tahfidz"),
                ("/tahfidz/laporan", "Laporan Lengkap"),
                *umum,
            )
        return umum
    if data.get("role") == "guru_bk":
        menu = [("/bk/", "Rapor BK")]
        if _punya_mapel(data):
            menu.append(("/presensi/hasil-belajar", "Hasil Belajar"))
        menu.append(("/presensi/ganti-password", "Ganti Password"))
        return tuple(menu)
    if data.get("role") == "guru_pengampu":
        return (
            ("/presensi/hasil-belajar", "Hasil Belajar"),
            ("/presensi/ganti-password", "Ganti Password"),
        )
    if data.get("role") == "guru_piket":
        menu = []
        if _guru_bk(data):
            menu.append(("/bk/", "Rapor BK"))
        menu.extend((
            ("/presensi/presensi", "Form Presensi"),
            ("/presensi/tata-tertib", "Tata Tertib"),
            ("/presensi/laporan-harian", "Laporan Harian"),
            ("/presensi/rekap-bulanan", "Rekap Bulanan"),
        ))
        if _punya_mapel(data):
            menu.append(("/presensi/hasil-belajar", "Hasil Belajar"))
        menu.append(("/presensi/ganti-password", "Ganti Password"))
        return tuple(menu)
    try:
        punya = akses_username(data.get("username") or "")
    except Exception:
        return (("/", "Beranda"),)
    return tuple(item for item in _MENU if item[0] == "/" or item[0].strip("/") in punya)


def _bebas_rawat(path):
    return path in {"/login", "/logout"} or path.startswith("/static/")


def _portal_rawat(path):
    for awalan in ("/presensi", "/erapor", "/tahfidz", "/bk", "/inventaris"):
        if path == awalan or path.startswith(awalan + "/"):
            return True
    return False


def _tulisan_rawat(admin):
    tautan = '<p><a href="/">Kembali ke beranda</a></p>' if admin else '<p><a href="/login">Masuk</a></p>'
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Maintenance · SMARTMU 22</title>
<style>
body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#f3efe6;color:#1c2823;font-family:"Segoe UI",Calibri,sans-serif}}
main{{width:min(460px,calc(100% - 32px));background:#fffdf8;border:1px solid #e3dccb;border-radius:20px;padding:32px 28px;text-align:center}}
img{{width:72px;height:72px;object-fit:contain}}
h1{{margin:8px 0 0;color:#0c4f3b;font-size:1.8rem}}
p{{line-height:1.5;color:#5d6b64}}
a{{color:#0c4f3b;font-weight:700}}
</style>
</head>
<body>
<main>
<img src="/static/logo-smpm22.png" alt="Logo SMP Muhammadiyah 22">
<p>SMP Muhammadiyah 22 Setiabudi Pamulang</p>
<h1>Maintenance</h1>
<p>Semua portal sedang dalam pemeliharaan. Silakan buka kembali setelah pemeliharaan selesai.</p>
{tautan}
</main>
</body>
</html>"""
    return html.encode("utf-8")


def _batang(path, masuk, menu):
    tautan = []
    for href, nama in menu:
        nyala = " on" if (href == "/" and path in {"/", "/login"}) or (
            href != "/" and (path == href.rstrip("/") or path.startswith(href))
        ) else ""
        tautan.append(f'<a class="{nyala.strip()}" href="{href}">{nama}</a>')
    akun = '<a href="/logout">Keluar</a>' if masuk else '<a href="/login">Masuk</a>'
    html = (
        '<div id="smartmu-switch"><a class="nama" href="/">SMARTMU 22</a>'
        '<button type="button" id="smartmu-garis" aria-label="Buka menu" aria-expanded="false">'
        "<span></span><span></span><span></span></button><nav>"
        + "".join(tautan)
        + akun
        + "</nav></div>"
    )
    return _GAYA + html.encode("utf-8") + _SKRIP


class BatangPortal:
    def __init__(self, aplikasi):
        self.aplikasi = aplikasi

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO") or "/"
        data = baca_cookie(environ.get("HTTP_COOKIE", ""))
        if rawat_aktif():
            admin = bool(data and data.get("role") == "admin")
            if _portal_rawat(path) or (not admin and not _bebas_rawat(path)):
                tubuh = _tulisan_rawat(admin)
                start_response(
                    "503 SERVICE UNAVAILABLE",
                    [
                        ("Content-Type", "text/html; charset=utf-8"),
                        ("Content-Length", str(len(tubuh))),
                        ("Cache-Control", "no-store"),
                    ],
                )
                return [tubuh]
        ditolak = _tolak_portal(environ)
        if ditolak:
            start_response(
                "302 FOUND",
                [("Location", ditolak), ("Content-Length", "0")],
            )
            return [b""]
        masuk = "smartmu_sso=" in environ.get("HTTP_COOKIE", "")
        menu = _menu_untuk(environ)
        status = "500 INTERNAL SERVER ERROR"
        headers = []

        def mulai(status_baru, header_baru, exc_info=None):
            nonlocal status, headers
            status = status_baru
            headers = list(header_baru or [])

        isi = self.aplikasi(environ, mulai)
        try:
            tubuh = b"".join(isi)
        finally:
            if hasattr(isi, "close"):
                isi.close()

        jenis = ""
        for kunci, nilai in headers:
            if kunci.lower() == "content-type":
                jenis = nilai.lower()
        if "text/html" in jenis and b"<body" in tubuh.lower() and b"smartmu-switch" not in tubuh:
            awal = tubuh.lower().find(b"<body")
            selesai = tubuh.find(b">", awal)
            if selesai != -1:
                tubuh = tubuh[: selesai + 1] + _batang(path, masuk, menu) + tubuh[selesai + 1 :]
                headers = [
                    (kunci, nilai)
                    for kunci, nilai in headers
                    if kunci.lower() not in {"content-length", "transfer-encoding"}
                ]
                headers.append(("Content-Length", str(len(tubuh))))
        start_response(status, headers)
        return [tubuh]


def bangun():
    return BatangPortal(
        DispatcherMiddleware(
            PORTAL,
            {
                "/presensi": _wajib_garis_miring(_muat_presensi()),
                "/erapor": _wajib_garis_miring(_muat_erapor()),
                "/tahfidz": _wajib_garis_miring(_muat_tahfidz()),
                "/bk": _wajib_garis_miring(_muat_bk()),
                "/inventaris": _wajib_garis_miring(_muat_inventaris()),
            },
        )
    )


aplikasi = bangun()


if __name__ == "__main__":
    print("SMARTMU 22 siap di http://127.0.0.1:5000")
    run_simple("127.0.0.1", 5000, aplikasi, use_debugger=True, use_reloader=False)
