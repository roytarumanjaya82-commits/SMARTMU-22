"""Launcher lokal. Produksi memakai: gunicorn wsgi:aplikasi"""

if __name__ == "__main__":
    from werkzeug.serving import run_simple

    from wsgi import aplikasi

    print("SMARTMU 22 siap di http://127.0.0.1:5000")
    run_simple("127.0.0.1", 5000, aplikasi, use_debugger=True, use_reloader=False)
