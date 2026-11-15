"""Penyimpanan gambar soal (upload file / tempel dari clipboard)."""

from __future__ import annotations

import base64
import re
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _upload_root() -> Path:
    root = Path(current_app.root_path) / "static" / "uploads" / "soal"
    root.mkdir(parents=True, exist_ok=True)
    return root


def simpan_gambar_file(file_storage: FileStorage, prefix: str = "soal") -> str | None:
    """Simpan FileStorage. Return path relatif ke static/, atau None."""
    if not file_storage or not file_storage.filename:
        return None
    name = secure_filename(file_storage.filename)
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("Format gambar harus PNG/JPG/GIF/WEBP.")
    filename = f"{prefix}_{uuid.uuid4().hex[:12]}{ext}"
    dest = _upload_root() / filename
    file_storage.save(dest)
    return f"uploads/soal/{filename}"


def simpan_gambar_base64(data_url: str, prefix: str = "soal") -> str | None:
    """Simpan data URL (hasil paste clipboard). Return path relatif ke static/."""
    raw = (data_url or "").strip()
    if not raw:
        return None
    match = re.match(
        r"^data:image/(png|jpeg|jpg|gif|webp);base64,(.+)$",
        raw,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise ValueError("Data gambar clipboard tidak valid.")
    ext = match.group(1).lower()
    if ext == "jpeg":
        ext = "jpg"
    if f".{ext}" not in ALLOWED_EXT:
        raise ValueError("Format gambar tidak didukung.")
    try:
        payload = base64.b64decode(match.group(2))
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Gagal membaca gambar dari clipboard.") from exc
    if len(payload) > 8 * 1024 * 1024:
        raise ValueError("Ukuran gambar maksimal 8 MB.")
    filename = f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}"
    dest = _upload_root() / filename
    dest.write_bytes(payload)
    return f"uploads/soal/{filename}"


def hapus_gambar_soal(rel_path: str | None) -> None:
    if not rel_path:
        return
    path = Path(current_app.root_path) / "static" / rel_path
    if path.is_file() and "uploads" in path.parts:
        try:
            path.unlink()
        except OSError:
            pass
