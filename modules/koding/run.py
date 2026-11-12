from koding import create_app
from koding.config import Config

app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print("Koding 7.5 · SMP Muhammadiyah 22")
    print(f"Akses lokal : http://127.0.0.1:{Config.FLASK_PORT}")
    print(f"Akses LAN   : http://<IP-KOMPUTER-INI>:{Config.FLASK_PORT}")
    print("Login guru  : guru / guru123")
    print("=" * 60)
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.DEBUG)
