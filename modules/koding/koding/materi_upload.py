import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_MATERI_EXT = {
    ".pdf": "pdf",
    ".doc": "doc",
    ".docx": "docx",
    ".ppt": "ppt",
    ".pptx": "pptx",
}

MAX_MATERI_BYTES = 25 * 1024 * 1024  # 25 MB


def ext_label(ext_or_tipe: str) -> str:
    t = (ext_or_tipe or "").lower().lstrip(".")
    return {
        "pdf": "PDF",
        "doc": "DOC",
        "docx": "DOCX",
        "ppt": "PPT",
        "pptx": "PPTX",
    }.get(t, t.upper() or "FILE")


def validate_materi_file(file_storage):
    if not file_storage or not file_storage.filename:
        return None, "Pilih file materi terlebih dahulu."
    original = secure_filename(file_storage.filename)
    if not original:
        return None, "Nama file tidak valid."
    ext = Path(original).suffix.lower()
    if ext not in ALLOWED_MATERI_EXT:
        return None, "Format harus PDF, DOC/DOCX, atau PPT/PPTX."
    file_storage.stream.seek(0, 2)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size <= 0:
        return None, "File kosong."
    if size > MAX_MATERI_BYTES:
        return None, "Ukuran file maksimal 25 MB."
    return {
        "original": original,
        "ext": ext,
        "tipe": ALLOWED_MATERI_EXT[ext],
        "ukuran": size,
    }, None


def save_materi_file(file_storage, tingkat: str, meta: dict) -> str:
    """Simpan file dan kembalikan path relatif dari UPLOAD_FOLDER."""
    folder = Path(current_app.config["UPLOAD_FOLDER"]) / "materi" / str(tingkat)
    folder.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}_{meta['original']}"
    abs_path = folder / stored
    file_storage.save(abs_path)
    return f"materi/{tingkat}/{stored}"


def absolute_materi_path(rel_path: str) -> Path:
    return Path(current_app.config["UPLOAD_FOLDER"]) / rel_path


def delete_materi_file(rel_path: str | None):
    if not rel_path:
        return
    path = absolute_materi_path(rel_path)
    try:
        if path.is_file():
            path.unlink()
    except OSError:
        pass
