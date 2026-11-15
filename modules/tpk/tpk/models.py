from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from tpk.extensions import db, login_manager

KELAS_CHOICES = (
    ("olimpiade", "Olimpiade"),
    ("tahfidz", "Tahfidz"),
    ("multimedia", "Multimedia"),
    ("internasional", "Internasional"),
    ("reguler", "Reguler"),
)

# Semua murid wajib mengikuti seluruh sesi wawancara ini
SESI_WAWANCARA = tuple(k for k, _ in KELAS_CHOICES)

ROLE_CHOICES = (
    ("admin", "Admin"),
    ("guru", "Guru Penguji"),
    ("guru_soal", "Guru Pembuat Soal"),
    ("murid", "Murid Peserta"),
    ("orang_tua", "Orang Tua"),
)

STATUS_PENDAFTARAN = (
    ("draft", "Draft"),
    ("terdaftar", "Terdaftar"),
    ("tes_susulan", "Menunggu Tes Susulan"),
    ("tes_selesai", "Tes Tertulis Selesai"),
    ("wawancara", "Menunggu Wawancara"),
    ("dinilai", "Sudah Dinilai"),
    ("ditetapkan", "Kelas Ditetapkan"),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(20), nullable=False, default="murid")
    kelas_penguji = db.Column(db.String(30))  # hanya untuk guru
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    murid_profile = db.relationship(
        "Murid",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="Murid.user_id",
    )
    anak_asuh = db.relationship(
        "Murid",
        back_populates="ortu_user",
        uselist=False,
        foreign_keys="Murid.ortu_user_id",
    )
    penilaian_dibuat = db.relationship("PenilaianWawancara", back_populates="guru")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def role_label(self) -> str:
        return dict(ROLE_CHOICES).get(self.role, self.role)

    @property
    def kelas_label(self) -> str:
        return dict(KELAS_CHOICES).get(self.kelas_penguji or "", "-")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Murid(db.Model):
    __tablename__ = "murid"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    ortu_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=True
    )
    nisn = db.Column(db.String(20), unique=True, nullable=False)
    nomor_urut = db.Column(db.String(20))
    tahun_ajaran = db.Column(db.String(20))
    gelombang = db.Column(db.String(50))
    tempat_lahir = db.Column(db.String(80))
    tanggal_lahir = db.Column(db.Date)
    jenis_kelamin = db.Column(db.String(10))
    alamat = db.Column(db.Text)
    no_hp = db.Column(db.String(20))
    nama_ortu = db.Column(db.String(150))
    no_hp_ortu = db.Column(db.String(20))
    alamat_ortu = db.Column(db.Text)
    asal_sekolah = db.Column(db.String(150))
    pilihan_kelas_1 = db.Column(db.String(30), nullable=False)
    pilihan_kelas_2 = db.Column(db.String(30))
    kelas_ditetapkan = db.Column(db.String(30))
    # Usulan penempatan sistem (sebelum ACC admin)
    kelas_usulan = db.Column(db.String(30))
    skor_penempatan = db.Column(db.Float)
    acc_penempatan = db.Column(db.Boolean, default=False)
    acc_at = db.Column(db.DateTime)
    status = db.Column(db.String(30), default="terdaftar")
    nilai_psikotes = db.Column(db.Float)  # skala 1–100 (hasil konversi dari mentah 0–165)
    catatan_psikotes = db.Column(db.Text)
    catatan_admin = db.Column(db.Text)
    # Berhalangan hadir pada jadwal tes → ikut tes susulan
    is_tes_susulan = db.Column(db.Boolean, default=False)
    alasan_susulan = db.Column(db.Text)
    tanggal_susulan = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship(
        "User", back_populates="murid_profile", foreign_keys=[user_id]
    )
    ortu_user = db.relationship(
        "User", back_populates="anak_asuh", foreign_keys=[ortu_user_id]
    )
    jawaban_tes = db.relationship("JawabanTes", back_populates="murid", cascade="all, delete-orphan")
    penilaian = db.relationship(
        "PenilaianWawancara", back_populates="murid", cascade="all, delete-orphan"
    )

    @property
    def pilihan1_label(self) -> str:
        return dict(KELAS_CHOICES).get(self.pilihan_kelas_1, self.pilihan_kelas_1)

    @property
    def pilihan2_label(self) -> str:
        return dict(KELAS_CHOICES).get(self.pilihan_kelas_2 or "", "-")

    @property
    def kelas_akhir_label(self) -> str:
        return dict(KELAS_CHOICES).get(self.kelas_ditetapkan or "", "Belum ditetapkan")

    @property
    def kelas_usulan_label(self) -> str:
        return dict(KELAS_CHOICES).get(self.kelas_usulan or "", "Belum diusulkan")

    @property
    def status_label(self) -> str:
        return dict(STATUS_PENDAFTARAN).get(self.status, self.status)

    def _sesi_tes_map(self) -> dict:
        return {s.kelas_tujuan: s for s in (self.sesi_tes or [])}

    def sesi_tes_kelas(self, kelas: str) -> Optional["SesiTesMurid"]:
        return self._sesi_tes_map().get(kelas)

    def tes_kelas_selesai(self, kelas: str) -> bool:
        sesi = self.sesi_tes_kelas(kelas)
        if sesi:
            return sesi.status == "selesai"
        # Kompatibilitas data lama: ada jawaban = dianggap selesai
        jawaban = [
            j
            for j in (self.jawaban_tes or [])
            if j.soal and j.soal.kelas_tujuan == kelas
        ]
        return bool(jawaban)

    def jumlah_jawaban_kelas(self, kelas: str) -> int:
        return sum(
            1
            for j in (self.jawaban_tes or [])
            if j.soal and j.soal.kelas_tujuan == kelas
        )

    def ringkas_tes_tertulis(self, kelas: Optional[str] = None) -> dict:
        """Ringkasan tes tertulis (semua atau per kelas soal)."""
        jawaban = list(self.jawaban_tes or [])
        if kelas:
            jawaban = [
                j for j in jawaban if j.soal and j.soal.kelas_tujuan == kelas
            ]
            selesai = self.tes_kelas_selesai(kelas) if jawaban else False
        else:
            selesai = self.tes_tertulis_selesai()
        total = len(jawaban)
        if not total:
            return {"benar": 0, "total": 0, "skor": None, "selesai": False}
        benar = sum(1 for j in jawaban if j.is_benar)
        return {
            "benar": benar,
            "total": total,
            "skor": round((benar / total) * 100, 2) if selesai else None,
            "selesai": selesai,
            "terjawab": total,
        }

    def nilai_tes_per_kelas(self) -> dict:
        """Nilai tes tertulis per kelas soal (0-100), hanya yang sudah submit."""
        hasil = {}
        for kode, _label in KELAS_CHOICES:
            ringkas = self.ringkas_tes_tertulis(kode)
            if ringkas["selesai"] and ringkas["skor"] is not None:
                hasil[kode] = ringkas["skor"]
        return hasil

    def skor_tes_tertulis(self, kelas: Optional[str] = None) -> Optional[float]:
        if kelas:
            return self.ringkas_tes_tertulis(kelas)["skor"]
        per_kelas = self.nilai_tes_per_kelas()
        if not per_kelas:
            return self.ringkas_tes_tertulis()["skor"]
        return round(sum(per_kelas.values()) / len(per_kelas), 2)

    def kelas_tes_tersedia(self) -> list:
        """Kelas yang punya soal aktif (semua murid wajib mengerjakan)."""
        from tpk.extensions import db

        rows = (
            db.session.query(SoalTes.kelas_tujuan)
            .filter_by(is_active=True)
            .distinct()
            .all()
        )
        tersedia = {r[0] for r in rows}
        return [k for k, _ in KELAS_CHOICES if k in tersedia]

    def tes_tertulis_selesai(self) -> bool:
        """Selesai jika semua kelas yang punya soal sudah dikerjakan."""
        kelas_wajib = self.kelas_tes_tersedia()
        if not kelas_wajib:
            return False
        sudah = self.nilai_tes_per_kelas()
        return all(k in sudah for k in kelas_wajib)

    @property
    def progress_tes_label(self) -> str:
        wajib = self.kelas_tes_tersedia()
        if not wajib:
            return "0/0 kelas"
        sudah = self.nilai_tes_per_kelas()
        return f"{sum(1 for k in wajib if k in sudah)}/{len(wajib)} kelas"

    def skor_wawancara(self, kelas: Optional[str] = None) -> Optional[float]:
        items = self.penilaian
        if kelas:
            items = [p for p in items if p.kelas_tujuan == kelas]
        if not items:
            return None
        # Ambil nilai tertinggi jika ada lebih dari satu penilaian di kelas yang sama
        return round(max(p.nilai_akhir for p in items), 2)

    def nilai_wawancara_per_kelas(self) -> dict:
        """Nilai wawancara per sesi kelas (skala 0-100)."""
        hasil = {}
        for p in self.penilaian:
            prev = hasil.get(p.kelas_tujuan)
            if prev is None or p.nilai_akhir > prev:
                hasil[p.kelas_tujuan] = round(p.nilai_akhir, 2)
        return hasil

    def sesi_selesai(self) -> list:
        """Daftar kode sesi wawancara yang sudah dinilai."""
        return [k for k in SESI_WAWANCARA if k in self.nilai_wawancara_per_kelas()]

    def jumlah_sesi_selesai(self) -> int:
        return len(self.sesi_selesai())

    def wawancara_lengkap(self) -> bool:
        """True jika sudah melalui seluruh 5 sesi wawancara."""
        return self.jumlah_sesi_selesai() >= len(SESI_WAWANCARA)

    @property
    def progress_wawancara_label(self) -> str:
        return f"{self.jumlah_sesi_selesai()}/{len(SESI_WAWANCARA)} sesi"

    def _pilih_kelas_terbaik(self, nilai: dict) -> Optional[str]:
        if not nilai:
            return None
        terbaik = max(nilai.values())
        kandidat = [k for k, v in nilai.items() if v == terbaik]
        for pilihan in (self.pilihan_kelas_1, self.pilihan_kelas_2):
            if pilihan in kandidat:
                return pilihan
        for kode in SESI_WAWANCARA:
            if kode in kandidat:
                return kode
        return kandidat[0]

    def rekomendasi_dari_wawancara(self) -> Optional[str]:
        """Kelas dengan nilai wawancara tertinggi saja (tanpa tes tertulis)."""
        return self._pilih_kelas_terbaik(self.nilai_wawancara_per_kelas())

    @property
    def rekomendasi_wawancara_label(self) -> str:
        kelas = self.rekomendasi_dari_wawancara()
        if not kelas:
            return "Belum ada penilaian wawancara"
        label = dict(KELAS_CHOICES).get(kelas, kelas)
        if not self.wawancara_lengkap():
            return f"{label} (sementara)"
        return label

    def nilai_rekomendasi_wawancara(self) -> Optional[float]:
        kelas = self.rekomendasi_dari_wawancara()
        if not kelas:
            return None
        return self.skor_wawancara(kelas)

    def skor_psikotes(self) -> Optional[float]:
        """Skor psikotes tersimpan (skala 1–100)."""
        if self.nilai_psikotes is None:
            return None
        return round(float(self.nilai_psikotes), 2)

    def skor_psikotes_100(self) -> Optional[float]:
        """Psikotes untuk nilai gabungan (sudah skala 1–100)."""
        return self.skor_psikotes()

    def skor_gabungan_per_kelas(self) -> dict:
        """Skor gabungan per kelas memakai bobot khusus kelas tersebut.

        Rumus tiap kelas:
          skor = (tes×bt + wawancara×bw + psikotes×bp) / (bt+bw+bp)
        Bobot bt/bw/bp diambil dari Pengaturan per kelas.
        Psikotes sudah tersimpan di skala 1–100 (hasil konversi upload blanko).
        Komponen yang belum ada dinormalisasi ulang dari yang tersedia.
        Minimal butuh nilai wawancara agar kelas masuk perhitungan.
        """
        from tpk.utils import get_bobot_penilaian

        wawancara = self.nilai_wawancara_per_kelas()
        tes_map = self.nilai_tes_per_kelas()
        if not wawancara:
            return {}
        psikotes = self.skor_psikotes_100()
        hasil = {}
        for kelas, w in wawancara.items():
            if kelas not in SESI_WAWANCARA:
                continue
            bt, bw, bp = get_bobot_penilaian(kelas)
            komponen = [(float(w), bw)]
            t = tes_map.get(kelas)
            if t is not None:
                komponen.append((float(t), bt))
            if psikotes is not None:
                komponen.append((float(psikotes), bp))
            total_b = sum(b for _, b in komponen) or 1.0
            hasil[kelas] = round(
                sum(nilai * (bobot / total_b) for nilai, bobot in komponen), 2
            )
        return hasil

    def rekomendasi_kelas(self) -> Optional[str]:
        """Kelas dengan skor gabungan tertinggi = rekomendasi penempatan.

        Contoh: jika skor gabungan Multimedia paling tinggi di antara semua kelas,
        murid direkomendasikan ke Multimedia. Jika seri, prioritas pilihan murid.
        """
        gabungan = self.skor_gabungan_per_kelas()
        if gabungan:
            return self._pilih_kelas_terbaik(gabungan)
        return None

    @property
    def rekomendasi_kelas_label(self) -> str:
        kelas = self.rekomendasi_kelas()
        if not kelas:
            if self.tes_tertulis_selesai() and not self.jumlah_sesi_selesai():
                return "Menunggu wawancara"
            if not self.tes_tertulis_selesai() and self.jumlah_sesi_selesai():
                return f"{self.rekomendasi_wawancara_label} (tanpa tes tertulis)"
            return "Belum ada penilaian"
        label = dict(KELAS_CHOICES).get(kelas, kelas)
        lengkap = (
            self.tes_tertulis_selesai()
            and self.wawancara_lengkap()
            and self.skor_psikotes() is not None
        )
        if not lengkap:
            return f"{label} (sementara)"
        return label

    def nilai_rekomendasi(self) -> Optional[float]:
        """Skor gabungan kelas yang direkomendasikan."""
        kelas = self.rekomendasi_kelas()
        if not kelas:
            return None
        return self.skor_gabungan_per_kelas().get(kelas)

    def skor_akhir(self) -> Optional[float]:
        """Skor penempatan final = skor gabungan kelas rekomendasi."""
        return self.nilai_rekomendasi()

    def sinkronkan_status_wawancara(self) -> None:
        """Perbarui status berdasarkan kelengkapan 5 sesi wawancara."""
        if self.status == "ditetapkan":
            return
        if self.wawancara_lengkap():
            self.status = "dinilai"
        elif self.jumlah_sesi_selesai() > 0:
            self.status = "wawancara"
        elif self.tes_tertulis_selesai():
            self.status = "tes_selesai"


class SoalTes(db.Model):
    __tablename__ = "soal_tes"

    id = db.Column(db.Integer, primary_key=True)
    kelas_tujuan = db.Column(db.String(30), nullable=False, index=True)
    pertanyaan = db.Column(db.Text, nullable=False)
    # Path relatif di static/, contoh: uploads/soal/xxx.png
    gambar = db.Column(db.String(255))
    opsi_a = db.Column(db.Text, nullable=False)
    opsi_b = db.Column(db.Text, nullable=False)
    opsi_c = db.Column(db.Text, nullable=False)
    opsi_d = db.Column(db.Text, nullable=False)
    jawaban_benar = db.Column(db.String(1), nullable=False)  # A/B/C/D
    bobot = db.Column(db.Integer, default=1)
    # Kisi-kisi soal (ditampilkan ke admin / ortu / murid)
    materi = db.Column(db.String(200))
    indikator = db.Column(db.Text)
    level_kognitif = db.Column(db.String(20))  # C1..C6 / mudah-sedang-sulit
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    jawaban = db.relationship("JawabanTes", back_populates="soal", cascade="all, delete-orphan")

    @property
    def kelas_label(self) -> str:
        return dict(KELAS_CHOICES).get(self.kelas_tujuan, self.kelas_tujuan)

    @property
    def punya_gambar(self) -> bool:
        return bool(self.gambar)

    @property
    def ringkas_pertanyaan(self) -> str:
        teks = (self.pertanyaan or "").strip()
        if len(teks) <= 80:
            return teks
        return teks[:77] + "..."


class JawabanTes(db.Model):
    __tablename__ = "jawaban_tes"
    __table_args__ = (db.UniqueConstraint("murid_id", "soal_id", name="uq_jawaban_murid_soal"),)

    id = db.Column(db.Integer, primary_key=True)
    murid_id = db.Column(db.Integer, db.ForeignKey("murid.id"), nullable=False)
    soal_id = db.Column(db.Integer, db.ForeignKey("soal_tes.id"), nullable=False)
    jawaban = db.Column(db.String(1), nullable=False)
    is_benar = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    murid = db.relationship("Murid", back_populates="jawaban_tes")
    soal = db.relationship("SoalTes", back_populates="jawaban")


class KriteriaPenilaian(db.Model):
    __tablename__ = "kriteria_penilaian"

    id = db.Column(db.Integer, primary_key=True)
    kelas_tujuan = db.Column(db.String(30), nullable=False, index=True)
    nama_kriteria = db.Column(db.String(120), nullable=False)
    deskripsi = db.Column(db.Text)
    bobot = db.Column(db.Integer, default=20)  # persen
    skor_maks = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)

    detail_nilai = db.relationship(
        "DetailPenilaian", back_populates="kriteria", cascade="all, delete-orphan"
    )

    @property
    def kelas_label(self) -> str:
        return dict(KELAS_CHOICES).get(self.kelas_tujuan, self.kelas_tujuan)


class SoalWawancara(db.Model):
    __tablename__ = "soal_wawancara"

    id = db.Column(db.Integer, primary_key=True)
    kelas_tujuan = db.Column(db.String(30), nullable=False, index=True)
    aspek = db.Column(db.String(120))  # aspek penilaian terkait
    pertanyaan = db.Column(db.Text, nullable=False)
    panduan = db.Column(db.Text)  # panduan penilaian untuk guru
    bobot = db.Column(db.Integer, default=12)  # poin skor maks soal (total kelas 100)
    urutan = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    jawaban = db.relationship(
        "JawabanWawancara", back_populates="soal", cascade="all, delete-orphan"
    )

    @property
    def kelas_label(self) -> str:
        return dict(KELAS_CHOICES).get(self.kelas_tujuan, self.kelas_tujuan)


class PenilaianWawancara(db.Model):
    __tablename__ = "penilaian_wawancara"

    id = db.Column(db.Integer, primary_key=True)
    murid_id = db.Column(db.Integer, db.ForeignKey("murid.id"), nullable=False)
    guru_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    kelas_tujuan = db.Column(db.String(30), nullable=False)
    catatan = db.Column(db.Text)
    rekomendasi = db.Column(db.String(30))  # diterima / cadangan / ditolak
    nilai_akhir = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    murid = db.relationship("Murid", back_populates="penilaian")
    guru = db.relationship("User", back_populates="penilaian_dibuat")
    detail = db.relationship(
        "DetailPenilaian", back_populates="penilaian", cascade="all, delete-orphan"
    )
    jawaban_soal = db.relationship(
        "JawabanWawancara", back_populates="penilaian", cascade="all, delete-orphan"
    )

    @property
    def kelas_label(self) -> str:
        return dict(KELAS_CHOICES).get(self.kelas_tujuan, self.kelas_tujuan)


class JawabanWawancara(db.Model):
    """Catatan jawaban & skor tiap soal wawancara per murid."""

    __tablename__ = "jawaban_wawancara"
    __table_args__ = (
        db.UniqueConstraint("penilaian_id", "soal_id", name="uq_jawaban_wawancara_soal"),
    )

    id = db.Column(db.Integer, primary_key=True)
    penilaian_id = db.Column(
        db.Integer, db.ForeignKey("penilaian_wawancara.id"), nullable=False
    )
    soal_id = db.Column(db.Integer, db.ForeignKey("soal_wawancara.id"), nullable=False)
    jawaban_murid = db.Column(db.Text)  # ringkasan/jawaban yang dicatat guru
    skor = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    penilaian = db.relationship("PenilaianWawancara", back_populates="jawaban_soal")
    soal = db.relationship("SoalWawancara", back_populates="jawaban")


class DetailPenilaian(db.Model):
    __tablename__ = "detail_penilaian"

    id = db.Column(db.Integer, primary_key=True)
    penilaian_id = db.Column(
        db.Integer, db.ForeignKey("penilaian_wawancara.id"), nullable=False
    )
    kriteria_id = db.Column(
        db.Integer, db.ForeignKey("kriteria_penilaian.id"), nullable=False
    )
    skor = db.Column(db.Float, nullable=False)

    penilaian = db.relationship("PenilaianWawancara", back_populates="detail")
    kriteria = db.relationship("KriteriaPenilaian", back_populates="detail_nilai")


class Pengaturan(db.Model):
    __tablename__ = "pengaturan"

    id = db.Column(db.Integer, primary_key=True)
    kunci = db.Column(db.String(80), unique=True, nullable=False)
    nilai = db.Column(db.String(255), nullable=False)
    keterangan = db.Column(db.String(255))


class KunciTesGelombang(db.Model):
    """Password masuk & keluar pengerjaan soal per gelombang (reguler / susulan)."""

    __tablename__ = "kunci_tes_gelombang"
    __table_args__ = (
        db.UniqueConstraint(
            "tahun_ajaran",
            "gelombang",
            "jenis",
            name="uq_kunci_tes_tahun_gelombang_jenis",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    tahun_ajaran = db.Column(db.String(20), nullable=False, index=True)
    gelombang = db.Column(db.String(50), nullable=False, index=True)
    # reguler = jadwal utama; susulan = murid berhalangan hadir
    jenis = db.Column(db.String(20), nullable=False, default="reguler")
    password_masuk = db.Column(db.String(80), nullable=False, default="MASUK123")
    password_keluar = db.Column(db.String(80), nullable=False, default="KELUAR123")
    is_aktif = db.Column(db.Boolean, default=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def jenis_label(self) -> str:
        return "Tes Susulan" if self.jenis == "susulan" else "Tes Reguler"


class SesiTesMurid(db.Model):
    """Monitoring sesi pengerjaan tes tertulis per murid per kelas soal."""

    __tablename__ = "sesi_tes_murid"
    __table_args__ = (
        db.UniqueConstraint(
            "murid_id", "kelas_tujuan", name="uq_sesi_tes_murid_kelas"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    murid_id = db.Column(db.Integer, db.ForeignKey("murid.id"), nullable=False)
    kelas_tujuan = db.Column(db.String(30), nullable=False, index=True)
    # aktif = sedang/masih bisa dikerjakan; selesai = sudah submit
    status = db.Column(db.String(20), default="aktif", nullable=False)
    mulai_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen_at = db.Column(db.DateTime, default=datetime.utcnow)
    selesai_at = db.Column(db.DateTime)
    reset_count = db.Column(db.Integer, default=0)
    pelanggaran = db.Column(db.Integer, default=0)
    catatan_pelanggaran = db.Column(db.Text)
    user_agent = db.Column(db.String(255))
    butuh_password_keluar = db.Column(db.Boolean, default=False)

    murid = db.relationship(
        "Murid",
        backref=db.backref("sesi_tes", cascade="all, delete-orphan"),
    )

    @property
    def kelas_label(self) -> str:
        return dict(KELAS_CHOICES).get(self.kelas_tujuan, self.kelas_tujuan)

    @property
    def status_label(self) -> str:
        labels = {
            "aktif": "Sedang mengerjakan",
            "selesai": "Sudah submit",
        }
        return labels.get(self.status, self.status)

    @property
    def online(self) -> bool:
        if not self.last_seen_at or self.status != "aktif":
            return False
        return (datetime.utcnow() - self.last_seen_at).total_seconds() < 45