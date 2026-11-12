"""Jalur materi berbasis objek untuk membuat game — Kelas 7, 8, dan 9.

Kelas 7: objek sebagai data (dict) + fungsi + loop game teks
Kelas 8: class/object, method, inheritance untuk entitas game
Kelas 9: project game terpadu (state, multi-entity, save, capstone)
"""

# Urutan 11+ agar tidak menabrak kurikulum utama (1–10)
URUTAN_AWAL = 11

MATERI_K7 = [
    {
        "urutan": 11,
        "judul": "Game OOP: Objek dalam Dunia Game",
        "ringkasan": "Mengenal 'objek' game lewat dict: player, musuh, item.",
        "isi_html": """
        <h3>Apa hubungan objek dan game?</h3>
        <p>Di game, hampir semua hal adalah <strong>objek</strong>: pemain, musuh, koin, nyawa.
        Di Kelas 7 kita belum memakai <code>class</code>, tapi sudah bisa membuat objek dengan
        <strong>dictionary</strong> yang punya data lengkap.</p>
        <h3>Contoh objek player</h3>
        <pre>player = {"nama": "Hero", "hp": 100, "skor": 0, "x": 0, "y": 0}</pre>
        <h3>Mengapa penting?</h3>
        <p>Data terkumpul di satu tempat. Nanti di Kelas 8 data ini digabung dengan perilaku (method)
        menjadi class sungguhan.</p>
        <h3>Deliverable</h3>
        <p>Buat 1 dict player dan 1 dict musuh dengan minimal 4 field.</p>
        """,
        "contoh_kode": 'player = {"nama": "Hero", "hp": 100, "skor": 0, "x": 0}\nmusuh = {"nama": "Slime", "hp": 30, "x": 5}\nprint(player["nama"], "vs", musuh["nama"])\nprint("HP player:", player["hp"])',
    },
    {
        "urutan": 12,
        "judul": "Game OOP: Player, Skor, dan Fungsi",
        "ringkasan": "Mengelola aksi game dengan fungsi yang mengubah data objek.",
        "isi_html": """
        <h3>Perilaku = fungsi</h3>
        <p>Object punya data. Aksi game (tambah skor, kurangi HP) ditulis sebagai
        <strong>fungsi</strong> yang menerima objek lalu mengubahnya.</p>
        <h3>Pola penting</h3>
        <ul>
          <li><code>tambah_skor(player, poin)</code></li>
          <li><code>kena_damage(player, dmg)</code></li>
          <li><code>status(player)</code> — tampilkan ringkas</li>
        </ul>
        <h3>Catatan</h3>
        <p>Dict bisa diubah di dalam fungsi. Pastikan HP tidak negatif.</p>
        """,
        "contoh_kode": 'def tambah_skor(p, poin):\n    p["skor"] += poin\n\ndef kena_damage(p, dmg):\n    p["hp"] = max(0, p["hp"] - dmg)\n\nplayer = {"nama": "Hero", "hp": 100, "skor": 0}\ntambah_skor(player, 10)\nkena_damage(player, 25)\nprint(player)',
    },
    {
        "urutan": 13,
        "judul": "Game OOP: Loop Game Sederhana",
        "ringkasan": "Membangun game loop: tampil status → input → update → ulang.",
        "isi_html": """
        <h3>Apa itu game loop?</h3>
        <p>Inti hampir semua game: selama belum selesai, ulang terus siklus
        <strong>tampil → input → update</strong>.</p>
        <ol>
          <li>Tampilkan status player</li>
          <li>Terima perintah (gerak/serang/keluar)</li>
          <li>Ubah data objek</li>
          <li>Cek menang/kalah</li>
        </ol>
        <h3>Syarat berhenti</h3>
        <p>HP habis, skor tercapai, atau pemain memilih keluar.</p>
        """,
        "contoh_kode": 'player = {"hp": 50, "skor": 0}\nwhile player["hp"] > 0 and player["skor"] < 30:\n    print("HP", player["hp"], "skor", player["skor"])\n    aksi = "serang"  # simulasi input\n    if aksi == "serang":\n        player["skor"] += 10\n        player["hp"] -= 5\nprint("selesai", player)',
    },
    {
        "urutan": 14,
        "judul": "Game OOP: Nyawa, Item, dan Benturan Sederhana",
        "ringkasan": "Menambah aturan game: item heal dan cek posisi saling dekat.",
        "isi_html": """
        <h3>Item sebagai objek</h3>
        <pre>potion = {"nama": "Heal", "heal": 20, "x": 3}</pre>
        <h3>Benturan sederhana</h3>
        <p>Dua objek "bertabrakan" jika posisinya sama atau selisihnya kecil
        (untuk game teks/1D cukup bandingkan <code>x</code>).</p>
        <h3>Aturan contoh</h3>
        <ul>
          <li>Jika player menyentuh potion → HP bertambah, item hilang</li>
          <li>Jika menyentuh musuh → HP berkurang</li>
        </ul>
        """,
        "contoh_kode": 'def dekat(a, b):\n    return a["x"] == b["x"]\n\nplayer = {"hp": 80, "x": 3}\npotion = {"heal": 20, "x": 3, "aktif": True}\nif potion["aktif"] and dekat(player, potion):\n    player["hp"] += potion["heal"]\n    potion["aktif"] = False\nprint(player, potion["aktif"])',
    },
    {
        "urutan": 15,
        "judul": "Game OOP: Mini Game Teks Kelas 7",
        "ringkasan": "Proyek mini: gabungkan objek dict, fungsi, loop, dan aturan skor/HP.",
        "isi_html": """
        <h3>Tugas proyek</h3>
        <p>Buat game teks singkat (contoh: lawan slime / kumpulkan koin) dengan:</p>
        <ul>
          <li>1 objek player (dict)</li>
          <li>1 objek musuh atau item</li>
          <li>Minimal 3 fungsi aksi</li>
          <li>Game loop sampai menang/kalah</li>
        </ul>
        <h3>Rubrik singkat</h3>
        <p>Data objek jelas, loop berjalan, ada kondisi selesai, kode bisa dijalankan.</p>
        <p><em>Bekal ke Kelas 8:</em> dict + fungsi ini akan jadi class + method.</p>
        """,
        "contoh_kode": 'import random\nplayer = {"nama": "Hero", "hp": 40, "skor": 0}\nmusuh = {"nama": "Slime", "hp": 25}\nwhile player["hp"] > 0 and musuh["hp"] > 0:\n    dmg = random.randint(5, 12)\n    musuh["hp"] -= dmg\n    player["skor"] += dmg\n    if musuh["hp"] > 0:\n        player["hp"] -= random.randint(3, 8)\nprint("menang" if musuh["hp"] <= 0 else "kalah", player)',
    },
]

MATERI_K8 = [
    {
        "urutan": 11,
        "judul": "Game OOP: Class Player untuk Game",
        "ringkasan": "Mengubah dict player menjadi class dengan __init__ dan atribut.",
        "isi_html": """
        <h3>Dari Kelas 7 ke class</h3>
        <p>Di Kelas 7 player adalah dict. Di Kelas 8 kita buat <strong>class Player</strong>
        agar data dan perilaku menyatu.</p>
        <pre>class Player:
    def __init__(self, nama, hp=100):
        self.nama = nama
        self.hp = hp
        self.skor = 0</pre>
        <h3>Keuntungan</h3>
        <p>Banyak player bisa dibuat dari cetakan yang sama, masing-masing punya data sendiri.</p>
        """,
        "contoh_kode": 'class Player:\n    def __init__(self, nama, hp=100):\n        self.nama = nama\n        self.hp = hp\n        self.skor = 0\n\np1 = Player("Hero")\np2 = Player("Ninja", 80)\nprint(p1.nama, p1.hp)\nprint(p2.nama, p2.hp)',
    },
    {
        "urutan": 12,
        "judul": "Game OOP: Method Gerak, Serang, dan Heal",
        "ringkasan": "Menambah perilaku game pada object Player/Enemy.",
        "isi_html": """
        <h3>Method = aksi object</h3>
        <ul>
          <li><code>gerak(dx)</code> — ubah posisi</li>
          <li><code>serang(target)</code> — kurangi HP lawan, tambah skor</li>
          <li><code>heal(poin)</code> — pulihkan HP dengan batas maksimal</li>
        </ul>
        <h3>self</h3>
        <p>Method memakai <code>self</code> untuk mengakses atribut object yang sedang bertindak.</p>
        """,
        "contoh_kode": 'class Player:\n    def __init__(self, nama, hp=100):\n        self.nama = nama\n        self.hp = hp\n        self.skor = 0\n        self.x = 0\n    def gerak(self, dx):\n        self.x += dx\n    def serang(self, target, dmg=10):\n        target.hp = max(0, target.hp - dmg)\n        self.skor += dmg\n    def heal(self, poin):\n        self.hp = min(100, self.hp + poin)\n\nhero = Player("Hero")\nslime = Player("Slime", 30)\nhero.gerak(2)\nhero.serang(slime, 12)\nprint(hero.x, hero.skor, slime.hp)',
    },
    {
        "urutan": 13,
        "judul": "Game OOP: Inheritance Player dan Enemy",
        "ringkasan": "Pewarisan class untuk entitas game yang mirip tapi berbeda perilaku.",
        "isi_html": """
        <h3>Kenapa inheritance?</h3>
        <p>Player dan Enemy sama-sama punya HP dan nama, tetapi berbeda aksi.
        Buat class dasar <code>Entity</code>, lalu turunkan.</p>
        <pre>class Entity: ...
class Player(Entity): ...
class Enemy(Entity): ...</pre>
        <h3>Override</h3>
        <p>Enemy bisa punya method <code>serang</code> sendiri (misalnya damage acak).</p>
        """,
        "contoh_kode": 'class Entity:\n    def __init__(self, nama, hp):\n        self.nama = nama\n        self.hp = hp\n    def hidup(self):\n        return self.hp > 0\n\nclass Player(Entity):\n    def __init__(self, nama, hp=100):\n        super().__init__(nama, hp)\n        self.skor = 0\n\nclass Enemy(Entity):\n    def serang(self, target):\n        target.hp = max(0, target.hp - 8)\n\nh = Player("Hero")\ne = Enemy("Goblin", 40)\ne.serang(h)\nprint(h.hp, e.hidup())',
    },
    {
        "urutan": 14,
        "judul": "Game OOP: Game Loop dengan Banyak Object",
        "ringkasan": "Mengelola list object (musuh/item) di dalam game loop OOP.",
        "isi_html": """
        <h3>Banyak object</h3>
        <p>Game nyata jarang hanya 1 musuh. Simpan banyak Enemy dalam <strong>list</strong>,
        lalu update satu per satu tiap putaran.</p>
        <h3>Pola</h3>
        <ol>
          <li>Buat player</li>
          <li>Buat list musuh</li>
          <li>Loop: player bertindak → tiap musuh bertindak → buang yang HP habis</li>
        </ol>
        """,
        "contoh_kode": 'class Enemy:\n    def __init__(self, nama, hp):\n        self.nama = nama\n        self.hp = hp\n\nmusuh = [Enemy("Slime", 20), Enemy("Bat", 15)]\nfor m in musuh:\n    m.hp -= 10\nhidup = [m for m in musuh if m.hp > 0]\nprint(len(hidup), "musuh tersisa")\nfor m in hidup:\n    print(m.nama, m.hp)',
    },
    {
        "urutan": 15,
        "judul": "Game OOP: Mini Game Arena Kelas 8",
        "ringkasan": "Proyek mini RPG/arena CLI memakai class, inheritance, dan game loop.",
        "isi_html": """
        <h3>Tugas proyek</h3>
        <ul>
          <li>Class dasar Entity + turunan Player/Enemy</li>
          <li>Minimal 3 method aksi</li>
          <li>1–3 musuh dalam list</li>
          <li>Loop sampai menang/kalah + tampil skor akhir</li>
        </ul>
        <h3>Rubrik</h3>
        <p>OOP dipakai benar, loop stabil, ada kondisi selesai, output jelas.</p>
        <p><em>Bekal ke Kelas 9:</em> game ini dikembangkan jadi project dengan state, save, dan rubrik capstone.</p>
        """,
        "contoh_kode": 'class Entity:\n    def __init__(self, nama, hp):\n        self.nama, self.hp = nama, hp\n    def hidup(self):\n        return self.hp > 0\n\nclass Player(Entity):\n    def __init__(self, nama):\n        super().__init__(nama, 50)\n        self.skor = 0\n    def serang(self, e, dmg=12):\n        e.hp = max(0, e.hp - dmg)\n        self.skor += dmg\n\nclass Enemy(Entity):\n    def serang(self, p):\n        p.hp = max(0, p.hp - 7)\n\np = Player("Hero")\ne = Enemy("Orc", 35)\nwhile p.hidup() and e.hidup():\n    p.serang(e)\n    if e.hidup():\n        e.serang(p)\nprint("Menang" if p.hidup() else "Kalah", "skor", p.skor)',
    },
]

MATERI_K9 = [
    {
        "urutan": 11,
        "judul": "Game Project: Desain Entity & Scene",
        "ringkasan": "Merancang arsitektur project game: entity, scene, dan folder.",
        "isi_html": """
        <h3>Project mindset</h3>
        <p>Kelas 9 menggabungkan OOP Kelas 8 menjadi <strong>project game</strong> yang terstruktur.</p>
        <h3>Komponen utama</h3>
        <ul>
          <li><strong>Entity</strong> — object yang hidup di dunia game</li>
          <li><strong>Scene</strong> — layar/keadaan (menu, play, game over)</li>
          <li><strong>Game</strong> — pengatur utama yang menjalankan scene</li>
        </ul>
        <h3>Deliverable</h3>
        <p>Diagram singkat + daftar class yang akan dibuat.</p>
        """,
        "contoh_kode": 'class Scene:\n    def __init__(self, nama):\n        self.nama = nama\n    def update(self):\n        return self.nama\n\nclass Game:\n    def __init__(self):\n        self.scene = Scene("menu")\n    def ganti(self, nama):\n        self.scene = Scene(nama)\n\ng = Game()\nprint(g.scene.update())\ng.ganti("play")\nprint(g.scene.update())',
    },
    {
        "urutan": 12,
        "judul": "Game Project: State Machine (Menu–Play–Game Over)",
        "ringkasan": "Mengatur alur game dengan state agar tidak bercampur logika.",
        "isi_html": """
        <h3>State machine sederhana</h3>
        <p>Game punya keadaan: <code>menu</code> → <code>play</code> → <code>gameover</code>.
        Tiap state punya perilaku berbeda.</p>
        <h3>Manfaat</h3>
        <p>Input di menu tidak ikut menggerakkan player; di game over tidak menambah skor.</p>
        """,
        "contoh_kode": 'class Game:\n    def __init__(self):\n        self.state = "menu"\n        self.skor = 0\n    def mulai(self):\n        self.state = "play"\n        self.skor = 0\n    def update(self, aksi):\n        if self.state == "menu" and aksi == "start":\n            self.mulai()\n        elif self.state == "play" and aksi == "mati":\n            self.state = "gameover"\n        elif self.state == "play" and aksi == "poin":\n            self.skor += 1\n\ng = Game()\ng.update("start")\ng.update("poin")\ng.update("mati")\nprint(g.state, g.skor)',
    },
    {
        "urutan": 13,
        "judul": "Game Project: Multi-Entity & Collision",
        "ringkasan": "Mengelola banyak entity dan aturan tabrakan pada project game.",
        "isi_html": """
        <h3>World berisi banyak entity</h3>
        <p>Simpan player, musuh, dan item dalam koleksi. Tiap tick: gerak → cek collision → bersihkan mati.</p>
        <h3>Collision</h3>
        <p>Untuk game grid/teks: sama posisi. Untuk 1D/2D sederhana: jarak di bawah ambang.</p>
        """,
        "contoh_kode": 'class Ent:\n    def __init__(self, jenis, x, hp=1):\n        self.jenis, self.x, self.hp = jenis, x, hp\n\ndef tabrak(a, b):\n    return a.x == b.x\n\nplayer = Ent("player", 2, 10)\nitems = [Ent("coin", 2), Ent("coin", 5)]\nskor = 0\nsisa = []\nfor it in items:\n    if tabrak(player, it):\n        skor += 1\n    else:\n        sisa.append(it)\nprint("skor", skor, "sisa", len(sisa))',
    },
    {
        "urutan": 14,
        "judul": "Game Project: Highscore & Save JSON",
        "ringkasan": "Menyimpan skor tertinggi agar project game punya persistensi.",
        "isi_html": """
        <h3>Kenapa highscore?</h3>
        <p>Game terasa lengkap jika rekor tersimpan setelah ditutup — terapkan JSON dari Kelas 8/9.</p>
        <h3>Alur</h3>
        <ol>
          <li>Muat highscore saat mulai</li>
          <li>Bandingkan dengan skor akhir</li>
          <li>Jika lebih tinggi, simpan ulang</li>
        </ol>
        """,
        "contoh_kode": 'import json\n\ndef muat(teks=\'{"highscore": 0}\'):\n    return json.loads(teks)\n\ndef cek_rekor(data, skor):\n    if skor > data["highscore"]:\n        data["highscore"] = skor\n        return True, json.dumps(data)\n    return False, json.dumps(data)\n\ndata = muat()\nbaru, teks = cek_rekor(data, 42)\nprint(baru, teks)',
    },
    {
        "urutan": 15,
        "judul": "Game Project: Capstone Game OOP Kelas 9",
        "ringkasan": "Project akhir: game OOP terpadu dengan state, entity, collision, dan save.",
        "isi_html": """
        <h3>Capstone</h3>
        <p>Bangun game CLI/teks (atau web mini) yang menggabungkan seluruh jalur Game OOP 7–9.</p>
        <h3>Wajib ada</h3>
        <ul>
          <li>Class entity (player/musuh/item) dengan inheritance atau komposisi</li>
          <li>State menu–play–game over</li>
          <li>Minimal 2 jenis interaksi (serang/ambil item)</li>
          <li>Highscore tersimpan (JSON)</li>
          <li>README singkat + demo</li>
        </ul>
        <h3>Rubrik</h3>
        <p>Berjalan, OOP jelas, state rapi, ada save, dokumentasi, siap showcase.</p>
        """,
        "contoh_kode": 'class Game:\n    def __init__(self):\n        self.state = "menu"\n        self.skor = 0\n        self.highscore = 0\n    def main(self):\n        self.state = "play"\n        self.skor = 15  # simulasi hasil main\n        self.state = "gameover"\n        if self.skor > self.highscore:\n            self.highscore = self.skor\n\ng = Game()\ng.main()\nprint(g.state, "skor", g.skor, "HS", g.highscore)',
    },
]

SEMESTER_GAME = "Genap"  # jalur tambahan di semester Genap
