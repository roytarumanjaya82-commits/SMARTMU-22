"""Backup & restore database MySQL via SQL dump (tanpa wajib mysqldump)."""

from __future__ import annotations

import io
import re
from datetime import datetime
from typing import Iterable

from flask import current_app
from sqlalchemy import text

from tpk.extensions import db


def _escape_sql(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, datetime):
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
    if hasattr(value, "isoformat"):
        # date / datetime-like
        try:
            return f"'{value.isoformat(sep=' ')}'"
        except TypeError:
            return f"'{value.isoformat()}'"
    if isinstance(value, (bytes, bytearray, memoryview)):
        raw = bytes(value)
        return "0x" + raw.hex() if raw else "NULL"
    text_val = str(value)
    text_val = (
        text_val.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\x00", "")
    )
    return f"'{text_val}'"


def _list_tables() -> list[str]:
    rows = db.session.execute(text("SHOW TABLES")).fetchall()
    return [r[0] for r in rows]


def buat_backup_sql() -> tuple[bytes, str]:
    """Generate SQL dump penuh database aktif. Return (content, filename)."""
    cfg = current_app.config
    db_name = cfg.get("MYSQL_DATABASE", "tpk_smartmu22")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{db_name}_{stamp}.sql"

    out = io.StringIO()
    out.write("-- TPK SMARTMU22 Database Backup\n")
    out.write(f"-- Database: {db_name}\n")
    out.write(f"-- Created: {datetime.now().isoformat(timespec='seconds')}\n")
    out.write("SET NAMES utf8mb4;\n")
    out.write("SET FOREIGN_KEY_CHECKS=0;\n")
    out.write("SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO';\n\n")

    tables = _list_tables()
    for table in tables:
        create_row = db.session.execute(text(f"SHOW CREATE TABLE `{table}`")).fetchone()
        create_sql = create_row[1]
        out.write(f"-- ----------------------------\n")
        out.write(f"-- Table structure: `{table}`\n")
        out.write(f"-- ----------------------------\n")
        out.write(f"DROP TABLE IF EXISTS `{table}`;\n")
        out.write(f"{create_sql};\n\n")

        rows = db.session.execute(text(f"SELECT * FROM `{table}`")).mappings().all()
        if not rows:
            out.write(f"-- No data for `{table}`\n\n")
            continue

        out.write(f"-- ----------------------------\n")
        out.write(f"-- Data: `{table}` ({len(rows)} rows)\n")
        out.write(f"-- ----------------------------\n")
        cols = list(rows[0].keys())
        col_list = ", ".join(f"`{c}`" for c in cols)

        batch: list[str] = []
        for row in rows:
            values = ", ".join(_escape_sql(row[c]) for c in cols)
            batch.append(f"({values})")
            if len(batch) >= 100:
                out.write(
                    f"INSERT INTO `{table}` ({col_list}) VALUES\n"
                    + ",\n".join(batch)
                    + ";\n"
                )
                batch = []
        if batch:
            out.write(
                f"INSERT INTO `{table}` ({col_list}) VALUES\n"
                + ",\n".join(batch)
                + ";\n"
            )
        out.write("\n")

    out.write("SET FOREIGN_KEY_CHECKS=1;\n")
    content = out.getvalue().encode("utf-8")
    return content, filename


def _split_sql_statements(sql_text: str) -> Iterable[str]:
    """Pecah dump SQL menjadi statement (menghormati string literal)."""
    buf: list[str] = []
    in_single = False
    in_double = False
    escape = False
    i = 0
    length = len(sql_text)
    while i < length:
        ch = sql_text[i]
        if escape:
            buf.append(ch)
            escape = False
            i += 1
            continue
        if ch == "\\" and (in_single or in_double):
            buf.append(ch)
            escape = True
            i += 1
            continue
        if ch == "'" and not in_double:
            # MySQL '' escape inside string
            if in_single and i + 1 < length and sql_text[i + 1] == "'":
                buf.append("''")
                i += 2
                continue
            in_single = not in_single
            buf.append(ch)
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
            i += 1
            continue
        if ch == ";" and not in_single and not in_double:
            stmt = "".join(buf).strip()
            buf = []
            if stmt:
                yield stmt
            i += 1
            continue
        buf.append(ch)
        i += 1
    stmt = "".join(buf).strip()
    if stmt:
        yield stmt


def _bersihkan_statement(stmt: str) -> str | None:
    # Hapus komentar baris
    lines = []
    for line in stmt.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        if stripped.startswith("#"):
            continue
        lines.append(line)
    cleaned = "\n".join(lines).strip()
    if not cleaned:
        return None
    # Tolak perintah berbahaya di luar dump normal
    upper = cleaned.lstrip().upper()
    forbidden = (
        "DROP DATABASE",
        "CREATE DATABASE",
        "ALTER DATABASE",
        "GRANT ",
        "REVOKE ",
        "SHUTDOWN",
    )
    for bad in forbidden:
        if upper.startswith(bad):
            raise ValueError(f"Perintah tidak diizinkan dalam restore: {bad.strip()}")
    return cleaned


def restore_dari_sql(sql_bytes: bytes) -> dict:
    """Restore database dari konten file .sql. Return ringkasan."""
    try:
        sql_text = sql_bytes.decode("utf-8")
    except UnicodeDecodeError:
        sql_text = sql_bytes.decode("latin-1")

    # Buang BOM
    if sql_text.startswith("\ufeff"):
        sql_text = sql_text[1:]

    executed = 0
    connection = db.engine.raw_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        for raw in _split_sql_statements(sql_text):
            stmt = _bersihkan_statement(raw)
            if not stmt:
                continue
            cursor.execute(stmt)
            executed += 1
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        try:
            connection.close()
        except Exception:  # noqa: BLE001
            pass
        db.session.remove()
        db.engine.dispose()

    return {"statements": executed}
