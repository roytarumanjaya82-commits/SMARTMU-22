import os

from dotenv import load_dotenv

load_dotenv()

try:
    from pengaturan import (
        MYSQL_HOST as _HOST,
        MYSQL_PASSWORD as _PASSWORD,
        MYSQL_PORT as _PORT,
        MYSQL_USER as _USER,
        SECRET_KEY as _SECRET,
        TPK_DATABASE as _DB,
    )
except Exception:  # noqa: BLE001
    _SECRET = os.getenv("FLASK_SECRET_KEY") or os.getenv("SECRET_KEY", "dev-secret-tpk-smartmu22")
    _HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    _PORT = int(os.getenv("MYSQL_PORT", "3306"))
    _USER = os.getenv("MYSQL_USER", "root")
    _PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    _DB = os.getenv("TPK_DATABASE", os.getenv("MYSQL_DATABASE", "tpk_smartmu22"))


class Config:
    SECRET_KEY = _SECRET
    MYSQL_HOST = _HOST
    MYSQL_PORT = int(_PORT)
    MYSQL_USER = _USER
    MYSQL_PASSWORD = _PASSWORD
    MYSQL_DATABASE = _DB

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
