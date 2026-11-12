import pymysql
from pymysql.cursors import DictCursor
from flask import g, current_app


def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host=current_app.config["MYSQL_HOST"],
            port=current_app.config["MYSQL_PORT"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DB"],
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=False,
        )
    return g.db


def close_db(_=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, args=None, one=False):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, args or ())
        rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows


def execute(sql, args=None, commit=True):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, args or ())
        last_id = cur.lastrowid
        rowcount = cur.rowcount
    if commit:
        db.commit()
    return last_id, rowcount


def executemany(sql, args_list, commit=True):
    db = get_db()
    with db.cursor() as cur:
        cur.executemany(sql, args_list)
    if commit:
        db.commit()
