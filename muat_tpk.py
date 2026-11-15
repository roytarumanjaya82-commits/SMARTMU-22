"""Muat aplikasi TPK tanpa menimpa paket app Inventaris."""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / "modules" / "tpk"


def muat():
    sys.path.insert(0, str(FOLDER))
    try:
        for nama in list(sys.modules):
            if nama == "tpk" or nama.startswith("tpk."):
                del sys.modules[nama]
        paket = importlib.import_module("tpk")
        aplikasi = paket.create_app()
    finally:
        while str(FOLDER) in sys.path:
            sys.path.remove(str(FOLDER))
    return aplikasi
