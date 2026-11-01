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
    modul = _muat_berkas("presensi_app", ROOT / "modules" / "presensi" / "app.py")
    return modul.app


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
#smartmu-switch{position:fixed;top:0;left:0;right:0;z-index:5000;height:44px;display:flex;align-items:center;gap:10px;padding:0 12px;background:#0c4f3b;color:#f3efe6;font:600 14px/1 "Segoe UI",sans-serif}
#smartmu-switch a{color:#f3efe6;text-decoration:none;padding:6px 8px;border-radius:8px;white-space:nowrap}
#smartmu-switch a.on,#smartmu-switch a:hover{background:#fff;color:#0c4f3b}
#smartmu-switch nav{display:flex;gap:2px;overflow:auto;flex:1}
#smartmu-switch .nama{font-weight:800;letter-spacing:-.02em}
#smartmu-garis{display:none;margin-left:auto;width:42px;height:36px;border:0;background:transparent;padding:8px;flex-direction:column;justify-content:center;gap:5px;cursor:pointer}
#smartmu-garis span{display:block;height:2px;border-radius:2px;background:#f3efe6}
body{padding-top:44px !important}
.topbar{top:44px !important}
.sidebar{top:calc(44px + var(--header-h, 0px)) !important;height:calc(100vh - 44px - var(--header-h, 0px)) !important}
#app .app{height:calc(100vh - 44px) !important}
@media (max-width: 760px){
  #smartmu-garis{display:inline-flex}
  #smartmu-switch nav{display:none;position:absolute;top:44px;left:0;right:0;flex:none;flex-direction:column;gap:4px;max-height:calc(100dvh - 44px);overflow-y:auto;background:#0c4f3b;padding:8px 10px 14px;border-top:1px solid rgba(255,255,255,.16);box-shadow:0 16px 32px rgba(0,0,0,.2)}
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


def _batang(path, masuk):
    tautan = []
    for href, nama in _MENU:
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
        masuk = "smartmu_sso=" in environ.get("HTTP_COOKIE", "")
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
                tubuh = tubuh[: selesai + 1] + _batang(path, masuk) + tubuh[selesai + 1 :]
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
