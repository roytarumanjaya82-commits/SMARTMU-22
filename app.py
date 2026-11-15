"""Launcher lokal. Produksi memakai: gunicorn wsgi:aplikasi"""

import socket


def _ip_lan():
    alamat = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            utama = s.getsockname()[0]
            if utama and not utama.startswith("127."):
                alamat.append(utama)
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip and not ip.startswith("127.") and ip not in alamat:
                alamat.append(ip)
    except OSError:
        pass
    return alamat


if __name__ == "__main__":
    from werkzeug.serving import run_simple

    from wsgi import aplikasi

    print("SMARTMU 22 siap")
    print("  Komputer ini : http://127.0.0.1:5000")
    for ip in _ip_lan():
        print(f"  Satu WiFi    : http://{ip}:5000")
    run_simple("0.0.0.0", 5000, aplikasi, use_debugger=True, use_reloader=False)
