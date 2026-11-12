"""Seed jalur materi Game OOP untuk Kelas 7–9 (semester Genap, urutan 11–15)."""
import sys
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from koding.config import Config  # noqa: E402
from koding.kurikulum_game_oop import (  # noqa: E402
    MATERI_K7,
    MATERI_K8,
    MATERI_K9,
    SEMESTER_GAME,
)

KKM = 77
SEMESTER = SEMESTER_GAME
JUDUL_PREFIX = "Game OOP"  # untuk deteksi hapus ulang


def Q(q, a, b, c, d, kunci, materi):
    return {
        "question": q,
        "options": {"A": a, "B": b, "C": c, "D": d},
        "answer": kunci,
        "materi": materi,
    }


SOAL = {
    "7": [
        Q("Di Kelas 7, objek player game paling sederhana digambarkan dengan...", "Class wajib", "Dictionary berisi data player", "Hanya angka tanpa kunci", "File Excel saja", "B", "Objek"),
        Q("Field penting pada objek player biasanya mencakup...", "Hanya warna tema OS", "Nama, HP, skor, posisi", "Password WiFi", "Driver VGA", "B", "Objek"),
        Q("Fungsi kena_damage(player, dmg) berperan sebagai...", "Menghapus Python", "Perilaku yang mengubah data objek", "Membuat class inheritance", "Menyalakan Flask", "B", "Fungsi"),
        Q("HP player setelah damage sebaiknya...", "Boleh negatif tanpa batas", "Dibatasi minimal 0", "Selalu jadi 100", "Dihapus dari dict", "B", "Fungsi"),
        Q("Game loop pada dasarnya mengulang...", "Install ulang OS", "Tampil status → input → update", "Hanya print sekali", "Query SQL wajib", "B", "Loop"),
        Q("Game loop berhenti jika...", "Tidak ada kondisi", "HP habis / menang / pemain keluar", "Dict kosong wajib", "Import gagal saja", "B", "Loop"),
        Q("Item potion dalam game teks digambarkan sebagai...", "Object data (dict) dengan efek heal", "Class Flask", "Gambar PNG saja", "Password guru", "A", "Item"),
        Q("Benturan sederhana 1D bisa dicek dengan...", "Membandingkan posisi x", "Menghapus semua variabel", "Mengganti interpreter", "Matikan loop", "A", "Item"),
        Q("Mini game Kelas 7 wajib punya...", "Supercomputer", "Objek dict + fungsi + loop selesai", "Hanya komentar", "Tanpa kondisi menang", "B", "Proyek"),
        Q("Bekal Kelas 7 menuju OOP sungguhan adalah...", "Dict + fungsi aksi", "Hanya HTML", "Hanya CSS", "Tanpa data", "A", "Proyek"),
        Q("player['skor'] += 10 artinya...", "Menghapus skor", "Menambah skor objek player", "Membuat class baru", "Menutup game", "B", "Fungsi"),
        Q("max(0, hp - dmg) berguna untuk...", "Mencegah HP negatif", "Menaikkan damage", "Mengacak skor", "Menghapus musuh", "A", "Fungsi"),
        Q("Status ditampilkan tiap putaran agar...", "Pemain tahu kondisi game", "Python lebih lambat", "Dict rusak", "Loop berhenti", "A", "Loop"),
        Q("Jika potion sudah diambil, flag aktif sebaiknya...", "True terus", "False agar tidak double heal", "Dihapus dari RAM fisik", "Jadi class", "B", "Item"),
        Q("Proyek mini game teks dinilai dari...", "Berjalan + objek jelas + ada akhir", "Hanya nama file panjang", "Hanya warna", "Tanpa output", "A", "Proyek"),
        Q("Musuh sebagai dict berbeda dari player karena...", "Field/peran beda meski bentuk data mirip", "Tidak boleh punya HP", "Wajib tanpa nama", "Harus class di Kelas 7", "A", "Objek"),
        Q("random dipakai di mini battle untuk...", "Damage/aksi tidak monoton", "Menghapus loop", "Membuat GUI wajib", "Encrypt JSON", "A", "Proyek"),
        Q("Fungsi status(player) sebaiknya...", "Menampilkan ringkas data objek", "Menghapus player", "Install paket", "Ganti OS", "A", "Fungsi"),
        Q("Syarat menang contoh kumpulkan skor 30 artinya...", "Loop cek skor >= 30", "HP selalu 0", "Tanpa skor", "Hanya 1 print", "A", "Loop"),
        Q("Materi Game OOP Kelas 7 fokus pada...", "Fondasi objek data sebelum class", "Flask penuh", "Inheritance wajib", "API JSON saja", "A", "Objek"),
    ],
    "8": [
        Q("Class Player menggantikan dict Kelas 7 agar...", "Data dan perilaku menyatu dalam object", "Dict dilarang selamanya", "Tanpa atribut", "Tanpa method", "A", "Class"),
        Q("__init__ pada Player berguna untuk...", "Mengisi atribut saat object dibuat", "Menghapus game loop", "Membuka port 80", "Matikan inheritance", "A", "Class"),
        Q("Method serang(target) adalah contoh...", "Perilaku object", "Variabel global wajib", "File CSS", "Query MySQL", "A", "Method"),
        Q("self.x += dx pada method gerak berarti...", "Menggeser posisi object itu sendiri", "Menghapus musuh", "Membuat scene", "Menyimpan JSON", "A", "Method"),
        Q("Inheritance Entity → Player/Enemy bermanfaat karena...", "Sifat bersama dipakai ulang, beda di turunan", "Menghapus semua class", "Melarang method", "Wajib tanpa HP", "A", "Inheritance"),
        Q("Override method serang pada Enemy artinya...", "Enemy punya perilaku serang sendiri", "Player hilang", "Dict wajib", "Loop berhenti", "A", "Inheritance"),
        Q("List musuh dipakai agar...", "Banyak object dikelola dalam loop", "Hanya 1 musuh selamanya", "Tanpa filter", "Tanpa HP", "A", "Loop OOP"),
        Q("Filter musuh hidup memakai...", "List comprehension / cek hp > 0", "Hapus Python", "Sort nama wajib", "JSON encrypt", "A", "Loop OOP"),
        Q("Mini game arena Kelas 8 menekankan...", "Class + inheritance + loop sampai selesai", "Hanya print hello", "Tanpa skor", "Tanpa Enemy", "A", "Arena"),
        Q("super().__init__ dipakai untuk...", "Memanggil constructor class induk", "Menghapus induk", "Buat file HTML", "Matikan assert", "A", "Inheritance"),
        Q("heal membatasi HP maksimal agar...", "Tidak melebihi batas wajar", "HP negatif", "Skor nol", "Enemy hilang", "A", "Method"),
        Q("hidup() pada Entity mengembalikan...", "True jika hp > 0", "Selalu False", "Nama file", "JSON", "A", "Inheritance"),
        Q("p1 dan p2 dari class yang sama...", "Punya data atribut masing-masing", "Selalu berbagi HP wajib", "Tidak boleh beda nama", "Wajib musuh", "A", "Class"),
        Q("Game loop OOP berbeda dari Kelas 7 karena...", "Aksi dipanggil lewat method object", "Tidak boleh ada loop", "Tanpa kondisi", "Wajib Flask", "A", "Loop OOP"),
        Q("Rubrik arena menilai...", "OOP benar, loop stabil, ada akhir", "Hanya font", "Hanya emoji", "Tanpa output", "A", "Arena"),
        Q("Enemy.serang(player) mengubah...", "HP player", "Nama class", "Versi Python", "KKM rapor", "A", "Method"),
        Q("Komposisi list + object mendukung...", "Wave musuh / banyak entitas", "Hanya 1 variabel int", "Tanpa class", "Tanpa skor", "A", "Loop OOP"),
        Q("Dari jalur ini bekal ke Kelas 9 adalah...", "Game OOP siap dikembangkan jadi project", "Membuang class", "Hanya dict lagi", "Tanpa state", "A", "Arena"),
        Q("Atribut skor biasanya ada di...", "Player", "Setiap spasi indentasi", "Modul math saja", "CSS", "A", "Class"),
        Q("Method hidup membantu...", "Cek object masih aktif di battle", "Menghapus inheritance", "Buat template HTML", "Matikan JSON", "A", "Inheritance"),
    ],
    "9": [
        Q("Scene dalam project game mewakili...", "Keadaan/layar seperti menu atau play", "Password root", "Driver printer", "File BIOS", "A", "Desain"),
        Q("Class Game biasanya berperan sebagai...", "Pengatur utama yang menjalankan scene/state", "Penyimpan CSS", "Penghapus OOP", "Modul VGA", "A", "Desain"),
        Q("State machine mencegah...", "Logika menu bercampur dengan play", "Adanya skor", "Adanya class", "Adanya JSON", "A", "State"),
        Q("Transisi menu → play terjadi saat...", "Aksi start/mulai", "HP selalu 0 di awal", "Import gagal", "Tanpa input", "A", "State"),
        Q("Collision multi-entity membutuhkan...", "Cek posisi/jarak antar object", "Hapus semua entity", "Satu print saja", "Tanpa loop", "A", "Collision"),
        Q("Entity coin yang diambil biasanya...", "Dihapus dari daftar sisa", "Menambah HP musuh", "Menutup state machine", "Menghapus README", "A", "Collision"),
        Q("Highscore disimpan ke JSON agar...", "Rekor tetap ada setelah program ditutup", "Game wajib online", "Class hilang", "State rusak", "A", "Save"),
        Q("Saat skor akhir > highscore, project harus...", "Memperbarui dan menyimpan rekor", "Menghapus player", "Reset OS", "Matikan loop", "A", "Save"),
        Q("Capstone game Kelas 9 wajib punya...", "Entity OOP + state + interaksi + save + README", "Hanya 1 print", "Tanpa dokumentasi", "Tanpa kondisi selesai", "A", "Capstone"),
        Q("Rubrik capstone menekankan...", "Berjalan, OOP jelas, state rapi, save, demo", "Hanya panjang nama file", "Hanya warna tombol", "Tanpa uji", "A", "Capstone"),
        Q("Folder project game membantu...", "Memisahkan entity, scene, dan data", "Menyembunyikan bug permanen", "Menghapus JSON", "Melarang class", "A", "Desain"),
        Q("Di state gameover, aksi play biasanya...", "Tidak menambah skor play lagi", "Wajib serang musuh", "Wajib gerak", "Menghapus highscore", "A", "State"),
        Q("List comprehension membersihkan entity mati karena...", "Hanya menyisakan yang masih relevan", "Menghapus Python", "Encrypt data", "Buat Flask", "A", "Collision"),
        Q("json.dumps pada highscore menghasilkan...", "Teks JSON siap disimpan", "Object Tkinter", "Query SQL", "Bitmap", "A", "Save"),
        Q("Capstone adalah lanjutan Kelas 7–8 karena...", "Menggabungkan objek, class, dan project utuh", "Membuang semua OOP", "Hanya dict tanpa loop", "Tanpa skor", "A", "Capstone"),
        Q("Minimal 2 interaksi di capstone contohnya...", "Serang dan ambil item", "Hanya komentar", "Hanya rename file", "Hanya warna", "A", "Capstone"),
        Q("g.ganti('play') pada desain scene artinya...", "Mengubah scene aktif ke play", "Menghapus Game", "Matikan inheritance", "Buat API", "A", "Desain"),
        Q("Persistensi highscore memakai bekal...", "JSON/file handling", "Hanya print", "Hanya tuple", "Tanpa data", "A", "Save"),
        Q("Update tiap tick biasanya berurutan...", "Gerak → collision → bersihkan mati", "Hapus class dulu", "Install OS", "Cetak laporan PDF wajib", "A", "Collision"),
        Q("Hasil belajar jalur Game OOP 7–9 adalah...", "Mampu membuat game berbasis objek bertingkat hingga project", "Hanya teori tanpa produk", "Hanya CSS", "Tanpa state/save", "A", "Capstone"),
    ],
}


def connect():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )


def ensure_schema(cur):
    for tabel in ("materi", "ujian", "kelas"):
        cur.execute(f"SHOW COLUMNS FROM {tabel} LIKE 'tingkat'")
        if not cur.fetchone():
            cur.execute(
                f"ALTER TABLE {tabel} ADD COLUMN tingkat ENUM('7','8','9') NOT NULL DEFAULT '7'"
            )
        else:
            cur.execute(
                f"ALTER TABLE {tabel} MODIFY tingkat ENUM('7','8','9') NOT NULL DEFAULT '7'"
            )


def hapus_jalur_lama(cur, tingkat):
    cur.execute(
        """
        SELECT id FROM materi
        WHERE tingkat=%s AND semester=%s AND urutan >= 11
          AND (judul LIKE 'Game OOP:%%' OR judul LIKE 'Game Project:%%')
        """,
        (tingkat, SEMESTER),
    )
    mid = [r["id"] for r in cur.fetchall()]
    cur.execute(
        """
        SELECT id FROM ujian
        WHERE tingkat=%s AND semester=%s
          AND (judul LIKE %s OR judul LIKE %s OR judul LIKE %s)
        """,
        (
            tingkat,
            SEMESTER,
            f"Latihan Game K{tingkat}%",
            f"UH Game K{tingkat}%",
            f"Sumatif Game K{tingkat}%",
        ),
    )
    uid = [r["id"] for r in cur.fetchall()]
    for u in uid:
        cur.execute("DELETE FROM soal WHERE ujian_id=%s", (u,))
    if uid:
        cur.execute(
            "DELETE FROM ujian WHERE id IN (%s)" % ",".join(["%s"] * len(uid)), uid
        )
    if mid:
        cur.execute(
            "DELETE FROM materi WHERE id IN (%s)" % ",".join(["%s"] * len(mid)), mid
        )


def insert_materi(cur, tingkat, items):
    ids = []
    for m in items:
        cur.execute(
            """
            INSERT INTO materi (tingkat, urutan, semester, judul, ringkasan, isi_html, contoh_kode, aktif)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """,
            (
                tingkat,
                m["urutan"],
                SEMESTER,
                m["judul"],
                m["ringkasan"],
                m["isi_html"],
                m["contoh_kode"],
            ),
        )
        ids.append(cur.lastrowid)
    return ids


def insert_ujian(cur, tingkat, judul, deskripsi, jenis, materi_id, soal_items, durasi, jumlah):
    cur.execute(
        "SELECT id FROM ujian WHERE tingkat=%s AND judul=%s AND semester=%s",
        (tingkat, judul, SEMESTER),
    )
    old = cur.fetchone()
    if old:
        cur.execute("DELETE FROM soal WHERE ujian_id=%s", (old["id"],))
        cur.execute("DELETE FROM ujian WHERE id=%s", (old["id"],))
    cur.execute(
        """
        INSERT INTO ujian
        (judul, deskripsi, jenis, semester, tingkat, materi_id, durasi_menit, jumlah_soal,
         nilai_kkm, acak_soal, tampil_pembahasan, aktif)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1,1,0)
        """,
        (judul, deskripsi, jenis, SEMESTER, tingkat, materi_id, durasi, jumlah, KKM),
    )
    uid = cur.lastrowid
    for i, q in enumerate(soal_items, start=1):
        cur.execute(
            """
            INSERT INTO soal
            (ujian_id, nomor, pertanyaan, opsi_a, opsi_b, opsi_c, opsi_d, kunci_jawaban, pembahasan, bobot, aktif)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1,0)
            """,
            (
                uid,
                i,
                q["question"],
                q["options"]["A"],
                q["options"]["B"],
                q["options"]["C"],
                q["options"]["D"],
                q["answer"],
                f"Materi terkait: {q.get('materi') or '-'}",
            ),
        )
    return uid


def seed_tingkat(cur, tingkat, materi_list, soal):
    hapus_jalur_lama(cur, tingkat)
    ids = insert_materi(cur, tingkat, materi_list)
    insert_ujian(
        cur,
        tingkat,
        f"Latihan Game K{tingkat} 1",
        f"Latihan jalur Game OOP kelas {tingkat}.",
        "latihan",
        ids[0],
        soal[0:8],
        25,
        8,
    )
    insert_ujian(
        cur,
        tingkat,
        f"Latihan Game K{tingkat} 2",
        f"Latihan lanjutan Game OOP kelas {tingkat}.",
        "latihan",
        ids[2],
        soal[6:14],
        25,
        8,
    )
    insert_ujian(
        cur,
        tingkat,
        f"Latihan Game K{tingkat} 3",
        f"Latihan proyek Game OOP kelas {tingkat}.",
        "latihan",
        ids[4],
        soal[12:20],
        25,
        8,
    )
    insert_ujian(
        cur,
        tingkat,
        f"UH Game K{tingkat}",
        f"Ulangan harian jalur Game OOP kelas {tingkat}.",
        "ulangan_harian",
        ids[0],
        soal[0:12],
        30,
        12,
    )
    insert_ujian(
        cur,
        tingkat,
        f"Sumatif Game K{tingkat}",
        f"Sumatif jalur Game OOP kelas {tingkat}.",
        "sumatif",
        None,
        soal,
        45,
        len(soal),
    )


def main():
    conn = connect()
    try:
        with conn.cursor() as cur:
            ensure_schema(cur)
            seed_tingkat(cur, "7", MATERI_K7, SOAL["7"])
            seed_tingkat(cur, "8", MATERI_K8, SOAL["8"])
            seed_tingkat(cur, "9", MATERI_K9, SOAL["9"])
        print("Jalur Game OOP Kelas 7–9 siap.")
        print("- 5 materi Genap (urutan 11–15) per tingkat")
        print("- 3 latihan + 1 UH + 1 sumatif per tingkat (default nonaktif)")
    finally:
        conn.close()

    sys.path.insert(0, str(ROOT / "scripts"))
    from enrich_contoh_materi import main as isi_contoh

    isi_contoh()


if __name__ == "__main__":
    main()
