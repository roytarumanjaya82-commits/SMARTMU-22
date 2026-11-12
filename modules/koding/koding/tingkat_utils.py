import re

TINGKAT_VALID = ("7", "8", "9")


def tingkat_dari_nama_kelas(nama_kelas: str) -> str:
    """Ambil tingkat dari nama kelas, contoh 7.5 -> 7, 8.1 -> 8, 9.3 -> 9."""
    if not nama_kelas:
        return "7"
    m = re.match(r"^\s*([789])", str(nama_kelas))
    return m.group(1) if m else "7"


def resolve_tingkat(session_tingkat=None, request_tingkat=None, default="7"):
    t = request_tingkat or session_tingkat or default
    return t if str(t) in TINGKAT_VALID else default
