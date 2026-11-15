"""Jalankan TPK secara mandiri (pengembangan). Di produksi pakai portal /tpk/."""

from tpk import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
