import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent.parent / ".env")

try:
    from pengaturan import (
        KODING_DATABASE,
        MYSQL_HOST as PORTAL_HOST,
        MYSQL_PASSWORD as PORTAL_PASSWORD,
        MYSQL_PORT as PORTAL_PORT,
        MYSQL_USER as PORTAL_USER,
        SECRET_KEY as PORTAL_SECRET,
    )
except ImportError:
    KODING_DATABASE = os.getenv("KODING_DATABASE", "koding_smpm22")
    PORTAL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    PORTAL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    PORTAL_USER = os.getenv("MYSQL_USER", "root")
    PORTAL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    PORTAL_SECRET = os.getenv("SECRET_KEY", "dev-koding-smpm22")


class Config:
    SECRET_KEY = PORTAL_SECRET or os.getenv("SECRET_KEY", "dev-koding-smpm22")
    MYSQL_HOST = PORTAL_HOST
    MYSQL_PORT = int(PORTAL_PORT)
    MYSQL_USER = PORTAL_USER
    MYSQL_PASSWORD = PORTAL_PASSWORD
    MYSQL_DB = os.getenv("KODING_DATABASE", KODING_DATABASE)
    UPLOAD_FOLDER = BASE_DIR / "koding" / "static" / "uploads"
    BLANKO_FOLDER = BASE_DIR / "data"
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(25 * 1024 * 1024)))
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "0") == "1"
    APP_BASE_URL = os.getenv("APP_BASE_URL", "").rstrip("/")


JENIS_UJIAN = {
    "latihan": "Latihan",
    "ulangan_harian": "Ulangan Harian",
    "sumatif": "Sumatif",
    "sts_ganjil": "Sumatif Tengah Semester Ganjil",
    "sts_genap": "Sumatif Tengah Semester Genap",
    "sas": "Sumatif Akhir Semester",
}
