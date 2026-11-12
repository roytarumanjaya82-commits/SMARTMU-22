"""Muat aplikasi Kelas Koding tanpa menimpa paket app Inventaris."""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / "modules" / "koding"


def muat():
    sys.path.insert(0, str(FOLDER))
    try:
        # Buang cache paket koding agar route/template baru (mis. Modul) pasti termuat.
        for nama in list(sys.modules):
            if nama == "koding" or nama.startswith("koding."):
                del sys.modules[nama]
        paket = importlib.import_module("koding")
        aplikasi = paket.create_app()
    finally:
        while str(FOLDER) in sys.path:
            sys.path.remove(str(FOLDER))
    return aplikasi
