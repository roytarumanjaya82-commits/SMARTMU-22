"""Muat aplikasi inventaris tanpa menimpa modul config Tahfidz."""

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / "modules" / "inventaris"


def muat():
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
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
        from app import create_app

        return create_app()
    finally:
        sys.path.remove(str(FOLDER))
        if konfigurasi_lama is not None:
            sys.modules["config"] = konfigurasi_lama
        else:
            sys.modules.pop("config", None)
