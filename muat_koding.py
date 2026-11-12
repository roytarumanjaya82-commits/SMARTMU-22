"""Muat aplikasi Kelas Koding tanpa menimpa paket app Inventaris."""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / "modules" / "koding"


def muat():
    sys.path.insert(0, str(FOLDER))
    try:
        if "koding" in sys.modules:
            paket = importlib.reload(sys.modules["koding"])
        else:
            paket = importlib.import_module("koding")
        aplikasi = paket.create_app()
    finally:
        while str(FOLDER) in sys.path:
            sys.path.remove(str(FOLDER))
    return aplikasi
