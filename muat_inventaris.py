"""Muat aplikasi inventaris tanpa menimpa modul config Tahfidz."""

import importlib
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / "modules" / "inventaris"
APP_FOLDER = FOLDER / "app"


def muat():
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

    # Root entry lama bernama app.py, sehingga `import app` mengambil file itu
    # — bukan packages inventaris. Sisihkan dulu, lalu biarkan inventaris
    # memakai nama `app` (dibutuhkan impor runtime seperti `from app.db`).
    disimpan = {
        nama: sys.modules.pop(nama)
        for nama in list(sys.modules)
        if nama == "app" or nama.startswith("app.")
    }
    konfigurasi_lama = sys.modules.get("config")

    spec = importlib.util.spec_from_file_location(
        "inventaris_config", FOLDER / "config.py"
    )
    konfigurasi = importlib.util.module_from_spec(spec)
    sys.modules["inventaris_config"] = konfigurasi
    sys.modules["config"] = konfigurasi
    spec.loader.exec_module(konfigurasi)

    sys.path.insert(0, str(FOLDER))
    try:
        paket = importlib.import_module("app")
        jalur = Path(getattr(paket, "__file__", "") or "").resolve().parent
        if jalur != APP_FOLDER.resolve():
            raise RuntimeError(
                f"Inventaris gagal dimuat: modul app mengarah ke {jalur}"
            )
        aplikasi = paket.create_app()
    finally:
        while str(FOLDER) in sys.path:
            sys.path.remove(str(FOLDER))

    # Jangan kembalikan app root — handler inventaris masih `from app...`.
    if "app" in disimpan:
        sys.modules["smartmu_root_app"] = disimpan["app"]

    # Inventaris butuh config-nya sendiri saat request.
    sys.modules["config"] = konfigurasi
    if konfigurasi_lama is not None and konfigurasi_lama is not konfigurasi:
        sys.modules.setdefault("smartmu_config_sebelum_inventaris", konfigurasi_lama)

    return aplikasi
