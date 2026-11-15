import re
import unicodedata
from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user

DEFAULT_PASSWORD_MURID = "murid123"
DEFAULT_PASSWORD_ORTU = "ortu123"

# Skor mentah psikotes di blanko (0–165); disimpan sebagai skala 1–100 setelah upload
PSIKOTES_MIN = 0
PSIKOTES_MAX = 165
PSIKOTES_SKALA_MIN = 1
PSIKOTES_SKALA_MAX = 100


def konversi_psikotes_ke_skala_100(nilai_mentah: float) -> float:
    """Ubah skor mentah 0–165 ke skala 1–100 (linear).

    Rumus: (nilai / 165) × 100, lalu dibatasi 1–100.
    Nilai mentah 0 → 1 (batas bawah skala).
    """
    raw = float(nilai_mentah)
    if raw <= 0:
        return float(PSIKOTES_SKALA_MIN)
    nilai = (raw / PSIKOTES_MAX) * float(PSIKOTES_SKALA_MAX)
    nilai = min(float(PSIKOTES_SKALA_MAX), max(float(PSIKOTES_SKALA_MIN), nilai))
    return round(nilai, 2)


def get_setting(kunci: str, default: str = "") -> str:
    from tpk.models import Pengaturan

    row = Pengaturan.query.filter_by(kunci=kunci).first()
    return row.nilai if row else default


def set_setting(kunci: str, nilai: str, keterangan=None) -> None:
    from tpk.extensions import db
    from tpk.models import Pengaturan

    row = Pengaturan.query.filter_by(kunci=kunci).first()
    if row:
        row.nilai = nilai
        if keterangan:
            row.keterangan = keterangan
    else:
        db.session.add(
            Pengaturan(kunci=kunci, nilai=nilai, keterangan=keterangan)
        )
    db.session.commit()


def get_tahun_ajaran() -> str:
    return get_setting("tahun_ajaran", "2026/2027")


def _parse_bobot_angka(value, default: float) -> float:
    try:
        return float(value if value not in (None, "") else default)
    except (TypeError, ValueError):
        return float(default)


def _normalisasi_bobot(bt: float, bw: float, bp: float) -> tuple:
    total = bt + bw + bp
    if total <= 0:
        return 30.0, 50.0, 20.0
    return (
        round(bt / total * 100, 2),
        round(bw / total * 100, 2),
        round(bp / total * 100, 2),
    )


def get_bobot_penilaian(kelas: str | None = None) -> tuple:
    """Bobot tes, wawancara, psikotes (dinormalisasi ke 100).

    Jika `kelas` diisi, pakai bobot khusus kelas tersebut.
    Jika belum diatur per kelas, jatuh ke bobot global.
    """
    bt = _parse_bobot_angka(get_setting("bobot_tes_tertulis", "30"), 30)
    bw = _parse_bobot_angka(get_setting("bobot_wawancara", "50"), 50)
    bp = _parse_bobot_angka(get_setting("bobot_psikotes", "20"), 20)

    if kelas:
        bt = _parse_bobot_angka(
            get_setting(f"bobot_tes_{kelas}", str(bt)), bt
        )
        bw = _parse_bobot_angka(
            get_setting(f"bobot_wawancara_{kelas}", str(bw)), bw
        )
        bp = _parse_bobot_angka(
            get_setting(f"bobot_psikotes_{kelas}", str(bp)), bp
        )
    return _normalisasi_bobot(bt, bw, bp)


def get_semua_bobot_kelas() -> dict:
    """Bobot penilaian untuk setiap kelas tujuan."""
    from tpk.models import KELAS_CHOICES

    return {kode: get_bobot_penilaian(kode) for kode, _label in KELAS_CHOICES}


def get_kuota_kelas(kelas: str) -> int:
    """Kuota penempatan untuk satu kelas (0 = tidak dibatasi)."""
    from tpk.models import KELAS_CHOICES

    if kelas not in dict(KELAS_CHOICES):
        return 0
    try:
        return max(0, int(float(get_setting(f"kuota_{kelas}", "0") or 0)))
    except (TypeError, ValueError):
        return 0


def get_semua_kuota_kelas() -> dict:
    from tpk.models import KELAS_CHOICES

    return {kode: get_kuota_kelas(kode) for kode, _ in KELAS_CHOICES}


def hitung_terisi_kelas(tahun: str | None = None) -> dict:
    """Jumlah murid yang sudah ditetapkan per kelas pada tahun ajaran."""
    from tpk.models import KELAS_CHOICES, Murid

    tahun = tahun or get_tahun_ajaran()
    hasil = {kode: 0 for kode, _ in KELAS_CHOICES}
    query = Murid.query.filter(
        Murid.kelas_ditetapkan.isnot(None),
        Murid.kelas_ditetapkan != "",
        (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)),
    )
    for m in query.all():
        if m.kelas_ditetapkan in hasil:
            hasil[m.kelas_ditetapkan] += 1
    return hasil


def sisa_kuota_kelas(kelas: str, tahun: str | None = None) -> int | None:
    """Sisa kuota kelas. None jika kuota tidak dibatasi (0)."""
    kuota = get_kuota_kelas(kelas)
    if kuota <= 0:
        return None
    terisi = hitung_terisi_kelas(tahun).get(kelas, 0)
    return max(kuota - terisi, 0)


def alokasi_penempatan_kuota(tahun: str | None = None, gelombang: str | None = None) -> dict:
    """Buat usulan penempatan berdasarkan skor gabungan tertinggi + kuota.

    Algoritma:
    1. Ambil murid yang punya skor gabungan (minimal wawancara).
    2. Urutkan menurut skor terbaik (desc).
    3. Tempatkan ke kelas skor tertinggi yang masih ada sisa kuota.
    4. Murid yang sudah ACC / ditetapkan tidak diubah ulang.

    Return: {diproses, diusulkan, dilewati, tanpa_slot, ringkas_kuota}
    """
    from tpk.extensions import db
    from tpk.models import KELAS_CHOICES, Murid, User

    tahun = tahun or get_tahun_ajaran()
    query = Murid.query.join(User, Murid.user_id == User.id).filter(
        (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None))
    )
    if gelombang:
        query = query.filter(Murid.gelombang == normalisasi_gelombang(gelombang))

    murid_list = query.order_by(User.nama_lengkap.asc()).all()
    kuota = get_semua_kuota_kelas()
    # Slot tersisa: mulai dari kuota dikurangi yang sudah ACC/ditetapkan
    terisi = {k: 0 for k, _ in KELAS_CHOICES}
    for m in murid_list:
        if m.acc_penempatan and m.kelas_ditetapkan in terisi:
            terisi[m.kelas_ditetapkan] += 1
        elif m.status == "ditetapkan" and m.kelas_ditetapkan in terisi:
            terisi[m.kelas_ditetapkan] += 1

    def sisa(kode: str) -> int | None:
        k = kuota.get(kode, 0)
        if k <= 0:
            return None  # unlimited
        return max(k - terisi.get(kode, 0), 0)

    kandidat = []
    dilewati = 0
    for m in murid_list:
        if m.acc_penempatan or m.status == "ditetapkan":
            dilewati += 1
            continue
        gabungan = m.skor_gabungan_per_kelas()
        if not gabungan:
            dilewati += 1
            continue
        # Ranking kelas: skor desc, tie-break pilihan murid
        ranking = sorted(
            gabungan.items(),
            key=lambda kv: (
                -kv[1],
                0 if kv[0] == m.pilihan_kelas_1 else 1 if kv[0] == m.pilihan_kelas_2 else 2,
            ),
        )
        terbaik_skor = ranking[0][1]
        kandidat.append((m, ranking, terbaik_skor))

    # Prioritas murid dengan skor terbaik lebih dulu
    kandidat.sort(key=lambda x: (-x[2], (x[0].user.nama_lengkap or "").lower()))

    diusulkan = 0
    tanpa_slot = 0
    for m, ranking, _skor in kandidat:
        ditempatkan = False
        for kelas, skor in ranking:
            slot = sisa(kelas)
            if slot is None or slot > 0:
                m.kelas_usulan = kelas
                m.skor_penempatan = skor
                m.acc_penempatan = False
                m.acc_at = None
                if slot is not None:
                    terisi[kelas] = terisi.get(kelas, 0) + 1
                diusulkan += 1
                ditempatkan = True
                break
        if not ditempatkan:
            m.kelas_usulan = None
            m.skor_penempatan = ranking[0][1] if ranking else None
            tanpa_slot += 1

    db.session.commit()
    ringkas = {
        kode: {
            "kuota": kuota.get(kode, 0),
            "terisi": terisi.get(kode, 0),
            "sisa": sisa(kode),
        }
        for kode, _ in KELAS_CHOICES
    }
    return {
        "diproses": len(kandidat),
        "diusulkan": diusulkan,
        "dilewati": dilewati,
        "tanpa_slot": tanpa_slot,
        "ringkas_kuota": ringkas,
    }


def get_gelombang_aktif() -> str:
    return normalisasi_gelombang(get_setting("gelombang_aktif", "1")) or "1"


def get_kunci_tes(
    tahun: str | None = None,
    gelombang: str | None = None,
    jenis: str = "reguler",
):
    """Ambil / buat password masuk-keluar tes (reguler atau susulan)."""
    from tpk.extensions import db
    from tpk.models import KunciTesGelombang

    tahun = tahun or get_tahun_ajaran()
    gelombang = normalisasi_gelombang(gelombang or get_gelombang_aktif()) or "1"
    jenis = "susulan" if jenis == "susulan" else "reguler"
    row = KunciTesGelombang.query.filter_by(
        tahun_ajaran=tahun, gelombang=gelombang, jenis=jenis
    ).first()
    if not row:
        defaults = (
            ("SUSULAN123", "KELUARSUSULAN", False)
            if jenis == "susulan"
            else ("MASUK123", "KELUAR123", True)
        )
        row = KunciTesGelombang(
            tahun_ajaran=tahun,
            gelombang=gelombang,
            jenis=jenis,
            password_masuk=defaults[0],
            password_keluar=defaults[1],
            is_aktif=defaults[2],
        )
        db.session.add(row)
        db.session.commit()
    return row


def kunci_tes_session_key(tahun: str, gelombang: str, jenis: str = "reguler") -> str:
    jenis = "susulan" if jenis == "susulan" else "reguler"
    return f"tes_masuk_ok:{tahun}:{gelombang}:{jenis}"


def tampilkan_kisi_kisi() -> bool:
    return (get_setting("tampilkan_kisi_kisi", "1") or "1") == "1"


def analisis_soal_tes(tahun: str | None = None, gelombang: str | None = None, kelas: str = ""):
    """Analisis jawaban per soal untuk gelombang tertentu."""
    from tpk.models import JawabanTes, KELAS_CHOICES, Murid, SoalTes

    tahun = tahun or get_tahun_ajaran()
    gelombang = normalisasi_gelombang(gelombang or get_gelombang_aktif()) or "1"
    query = SoalTes.query.filter_by(is_active=True)
    if kelas in dict(KELAS_CHOICES):
        query = query.filter_by(kelas_tujuan=kelas)
    soals = query.order_by(SoalTes.kelas_tujuan, SoalTes.id).all()

    murid_ids = [
        m.id
        for m in Murid.query.filter(
            (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)),
            Murid.gelombang == gelombang,
        ).all()
    ]
    rows = []
    for idx, soal in enumerate(soals, start=1):
        jawaban = JawabanTes.query.filter(
            JawabanTes.soal_id == soal.id,
            JawabanTes.murid_id.in_(murid_ids) if murid_ids else False,
        ).all() if murid_ids else []
        total = len(jawaban)
        benar = sum(1 for j in jawaban if j.is_benar)
        sebaran = {"A": 0, "B": 0, "C": 0, "D": 0}
        for j in jawaban:
            if j.jawaban in sebaran:
                sebaran[j.jawaban] += 1
        rows.append(
            {
                "no": idx,
                "soal": soal,
                "total": total,
                "benar": benar,
                "salah": max(total - benar, 0),
                "persen_benar": round((benar / total) * 100, 1) if total else None,
                "sebaran": sebaran,
            }
        )
    return rows


def daftar_kisi_kisi(kelas: str = ""):
    """Daftar kisi-kisi soal aktif (opsional filter kelas)."""
    from tpk.models import KELAS_CHOICES, SoalTes

    query = SoalTes.query.filter_by(is_active=True)
    if kelas in dict(KELAS_CHOICES):
        query = query.filter_by(kelas_tujuan=kelas)
    return query.order_by(SoalTes.kelas_tujuan, SoalTes.id).all()


def _parse_daftar_gelombang(raw: str) -> list:
    items = []
    for part in (raw or "").split(","):
        g = normalisasi_gelombang(part)
        if g and g not in items:
            items.append(g)
    return items


def _urut_gelombang(items: list) -> list:
    """Urutkan angka dulu, lalu teks."""
    angka = sorted([g for g in items if g.isdigit()], key=lambda x: int(x))
    teks = sorted([g for g in items if not g.isdigit()])
    return angka + teks


def get_daftar_gelombang() -> list:
    """Gabungkan daftar pengaturan + gelombang yang sudah ada di data murid.

    Gelombang lama tidak pernah diganti/hilang hanya karena upload gelombang baru.
    """
    items = _parse_daftar_gelombang(get_setting("daftar_gelombang", "1,2,3"))
    try:
        from tpk.models import Murid

        tahun = get_tahun_ajaran()
        q = Murid.query.with_entities(Murid.gelombang).distinct()
        if tahun:
            q = q.filter(
                (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None))
            )
        for (g,) in q.all():
            g = normalisasi_gelombang(g)
            if g and g not in items:
                items.append(g)
    except Exception:  # noqa: BLE001
        pass
    return _urut_gelombang(items) or ["1", "2", "3"]


def tambah_gelombang_ke_daftar(*gelombang_list) -> list:
    """Tambah gelombang ke pengaturan tanpa menghapus gelombang yang sudah ada."""
    existing = _parse_daftar_gelombang(get_setting("daftar_gelombang", "1,2,3"))
    changed = False
    for raw in gelombang_list:
        g = normalisasi_gelombang(raw)
        if g and g not in existing:
            existing.append(g)
            changed = True
    if changed:
        set_setting(
            "daftar_gelombang",
            ",".join(_urut_gelombang(existing)),
            "Daftar gelombang dalam satu tahun ajaran",
        )
    return _urut_gelombang(existing)


# Nilai khusus filter/hapus untuk murid yang belum punya gelombang
GELOMBANG_KOSONG = "__kosong__"


def normalisasi_gelombang(value) -> str:
    """Seragamkan nilai gelombang, contoh: 'Gelombang 1' / '1' → '1'."""
    import re

    text = str(value or "").strip()
    if not text:
        return ""
    if text.lower() in (GELOMBANG_KOSONG, "tanpa", "kosong", "null", "-"):
        return GELOMBANG_KOSONG
    text = re.sub(r"(?i)^gelombang\s*", "", text).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def label_gelombang(value) -> str:
    g = normalisasi_gelombang(value)
    if not g:
        return "-"
    if g == GELOMBANG_KOSONG:
        return "Tanpa gelombang"
    if g.isdigit():
        return f"Gelombang {g}"
    return f"Gelombang {g}"


def is_gelombang_kosong(value) -> bool:
    return normalisasi_gelombang(value) == GELOMBANG_KOSONG


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                abort(403)
            if not current_user.is_active_user:
                flash("Akun Anda nonaktif.", "danger")
                return redirect(url_for("auth.logout"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


def redirect_by_role(user):
    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    if user.role == "guru":
        return redirect(url_for("guru.dashboard"))
    if user.role == "guru_soal":
        return redirect(url_for("guru_soal.soal_list"))
    if user.role == "orang_tua":
        return redirect(url_for("ortu.dashboard"))
    return redirect(url_for("murid.dashboard"))


def buat_username_ortu(murid, exclude_user_id=None) -> str:
    """Username orang tua: ortu.<username_anak> (unik)."""
    from tpk.models import User

    anak_user = getattr(murid, "user", None)
    dasar_anak = (anak_user.username if anak_user else "") or slug_nama(
        getattr(murid, "nisn", None) or "anak"
    )
    dasar = f"ortu.{dasar_anak}"
    kandidat = dasar
    counter = 2
    while True:
        query = User.query.filter_by(username=kandidat)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        if not query.first():
            return kandidat
        kandidat = f"{dasar}{counter}"
        counter += 1


def pastikan_akun_ortu(murid, commit: bool = False):
    """Buat / perbarui akun login orang tua untuk satu murid.

    Returns:
        (user, created: bool)
    """
    from tpk.extensions import db
    from tpk.models import User

    nama = (murid.nama_ortu or "").strip() or (
        f"Orang Tua {murid.user.nama_lengkap}" if murid.user else "Orang Tua"
    )

    if murid.ortu_user_id:
        ortu = db.session.get(User, murid.ortu_user_id)
        if ortu and ortu.role == "orang_tua":
            ortu.nama_lengkap = nama
            if commit:
                db.session.commit()
            return ortu, False

    username = buat_username_ortu(murid)
    ortu = User(
        username=username,
        nama_lengkap=nama,
        role="orang_tua",
        is_active_user=True,
    )
    ortu.set_password(DEFAULT_PASSWORD_ORTU)
    db.session.add(ortu)
    db.session.flush()
    murid.ortu_user_id = ortu.id
    if commit:
        db.session.commit()
    return ortu, True


def sinkronkan_akun_ortu(murid_list) -> dict:
    """Buat akun ortu untuk daftar murid. Return ringkasan."""
    from tpk.extensions import db

    dibuat = 0
    diperbarui = 0
    for murid in murid_list:
        _, created = pastikan_akun_ortu(murid, commit=False)
        if created:
            dibuat += 1
        else:
            diperbarui += 1
    db.session.commit()
    return {"dibuat": dibuat, "diperbarui": diperbarui}


def slug_nama(nama: str) -> str:
    """Ubah nama menjadi username dasar (huruf kecil tanpa spasi/simbol)."""
    text = unicodedata.normalize("NFKD", nama or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", "", text)
    return text or "murid"


def buat_username_dari_nama(nama_lengkap: str, exclude_user_id=None) -> str:
    """Username otomatis dari nama murid. Jika bentrok, tambah angka."""
    from tpk.models import User

    dasar = slug_nama(nama_lengkap)
    kandidat = dasar
    counter = 2
    while True:
        query = User.query.filter_by(username=kandidat)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        if not query.first():
            return kandidat
        kandidat = f"{dasar}{counter}"
        counter += 1