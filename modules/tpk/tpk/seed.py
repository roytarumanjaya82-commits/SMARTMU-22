from tpk.extensions import db
from tpk.models import KriteriaPenilaian, Pengaturan, SoalTes, SoalWawancara, User


KRITERIA_DEFAULT = {
    "olimpiade": [
        ("Pemahaman konsep dasar", "Penguasaan materi olimpiade sesuai bidang", 25),
        ("Kemampuan problem solving", "Cara menyelesaikan soal/tantangan logika", 25),
        ("Motivasi & ketekunan", "Semangat latihan dan komitmen belajar", 20),
        ("Prestasi akademik", "Nilai/riwayat lomba sebelumnya", 15),
        ("Komunikasi & sikap", "Kesantunan dan kejelasan menjawab", 15),
    ],
    "tahfidz": [
        ("Kelancaran bacaan Al-Qur'an", "Tajwid dan kelancaran tilawah", 30),
        ("Hafalan yang dimiliki", "Jumlah dan kualitas hafalan", 25),
        ("Motivasi tahfidz", "Niat dan komitmen menghafal", 20),
        ("Disiplin ibadah", "Kebiasaan shalat dan amalan harian", 15),
        ("Sikap & adab", "Kesopanan dan akhlak dalam wawancara", 10),
    ],
    "multimedia": [
        ("Minat & portofolio", "Hasil karya desain/video/editing", 30),
        ("Pemahaman dasar multimedia", "Konsep desain, video, atau fotografi", 25),
        ("Kreativitas", "Ide dan inovasi karya", 20),
        ("Motivasi belajar", "Alasan memilih kelas multimedia", 15),
        ("Komunikasi", "Kemampuan menjelaskan karya", 10),
    ],
    "internasional": [
        ("Kemampuan bahasa Inggris", "Speaking & comprehension dasar", 30),
        ("Wawasan global", "Pengetahuan umum internasional", 20),
        ("Motivasi kelas internasional", "Alasan dan tujuan belajar", 20),
        ("Kemampuan akademik", "Kesiapan materi pelajaran", 15),
        ("Sikap & kepercayaan diri", "Keberanian berbicara", 15),
    ],
    "reguler": [
        ("Kesiapan akademik", "Dasar matematika, IPA, bahasa", 30),
        ("Motivasi sekolah di SMARTMU", "Alasan memilih sekolah", 20),
        ("Disiplin & tanggung jawab", "Kebiasaan belajar dan perilaku", 20),
        ("Dukungan orang tua", "Kesiapan keluarga mendampingi", 15),
        ("Sikap & komunikasi", "Kesantunan wawancara", 15),
    ],
}

SOAL_WAWANCARA = {
    "olimpiade": [
        (
            1,
            "Motivasi & ketekunan",
            "Mengapa kamu tertarik masuk kelas Olimpiade di SMP Muhammadiyah 22?",
            "Perhatikan kejelasan alasan, minat belajar mendalam, dan komitmen latihan.",
        ),
        (
            2,
            "Pemahaman konsep dasar",
            "Jelaskan perbedaan antara bilangan prima dan bilangan komposit, lalu berikan contoh masing-masing.",
            "Nilai pemahaman konsep dasar matematika/sains, bukan sekadar hafalan.",
        ),
        (
            3,
            "Kemampuan problem solving",
            "Jika ada soal yang sulit dan belum pernah kamu temui, langkah apa yang akan kamu lakukan?",
            "Cari strategi berpikir sistematis: pahami soal, pecah masalah, coba cara lain, minta bimbingan.",
        ),
        (
            4,
            "Prestasi akademik",
            "Apakah kamu pernah mengikuti lomba akademik (matematika, IPA, atau lainnya)? Ceritakan pengalamanmu.",
            "Nilai riwayat prestasi/latihan, bukan hanya juara. Semangat ikut lomba juga dihitung.",
        ),
        (
            5,
            "Kemampuan problem solving",
            "Ada 3 kotak: satu berisi apel, satu jeruk, dan satu campuran. Semua label salah. Bagaimana cara menentukan isi masing-masing kotak dengan membuka hanya 1 kotak?",
            "Amati logika jawaban. Fokus pada proses berpikir, bukan hanya jawaban akhir.",
        ),
        (
            6,
            "Motivasi & ketekunan",
            "Berapa lama kamu biasanya belajar di rumah setiap hari, dan bagaimana caramu menjaga konsistensi?",
            "Nilai kedisiplinan, kebiasaan latihan, dan dukungan lingkungan.",
        ),
        (
            7,
            "Komunikasi & sikap",
            "Jika temanmu mengajak bermain padahal kamu harus latihan soal olimpiade, apa yang akan kamu lakukan?",
            "Perhatikan keseimbangan, kejujuran, dan sikap tanggung jawab.",
        ),
        (
            8,
            "Komunikasi & sikap",
            "Apa harapanmu jika diterima di kelas Olimpiade SMARTMU 22?",
            "Lihat visi jangka pendek/panjang dan kesungguhan mengikuti program sekolah.",
        ),
    ],
    "tahfidz": [
        (
            1,
            "Motivasi tahfidz",
            "Mengapa kamu ingin masuk kelas Tahfidz di SMP Muhammadiyah 22?",
            "Nilai niat, keikhlasan, dan komitmen menghafal Al-Qur'an.",
        ),
        (
            2,
            "Hafalan yang dimiliki",
            "Surah atau juz berapa yang sudah kamu hafal saat ini? Sebutkan dan bacakan sebagian.",
            "Catat jumlah hafalan, kelancaran, dan ketepatan bacaan.",
        ),
        (
            3,
            "Kelancaran bacaan Al-Qur'an",
            "Bacakan Surah Al-Fatihah atau surah pendek pilihanmu dengan tartil.",
            "Perhatikan makharijul huruf, tajwid dasar, kelancaran, dan adab membaca.",
        ),
        (
            4,
            "Hafalan yang dimiliki",
            "Bagaimana metode yang kamu pakai untuk menambah dan menjaga hafalan?",
            "Contoh: muroja'ah harian, setoran, menulis, mendengar murottal.",
        ),
        (
            5,
            "Disiplin ibadah",
            "Bagaimana kebiasaan shalat dan wirid harianmu di rumah?",
            "Nilai konsistensi ibadah dan kesadaran spiritual.",
        ),
        (
            6,
            "Motivasi tahfidz",
            "Jika hafalan terasa sulit atau mudah lupa, apa yang biasanya kamu lakukan?",
            "Cari sikap pantang menyerah, strategi muroja'ah, dan kesediaan dibimbing.",
        ),
        (
            7,
            "Sikap & adab",
            "Menurutmu, adab apa saja yang harus dimiliki seorang penghafal Al-Qur'an?",
            "Nilai pemahaman adab: jujur, rendah hati, menjaga lisan, hormat guru/orang tua.",
        ),
        (
            8,
            "Sikap & adab",
            "Apa komitmenmu jika diterima di kelas Tahfidz SMARTMU 22?",
            "Pastikan siap setoran rutin, muroja'ah, dan mengikuti program tahfidz sekolah.",
        ),
    ],
    "multimedia": [
        (
            1,
            "Motivasi belajar",
            "Mengapa kamu memilih kelas Multimedia? Apa yang paling kamu minati: desain, video, atau fotografi?",
            "Nilai kejelasan minat dan alasan memilih jalur multimedia.",
        ),
        (
            2,
            "Minat & portofolio",
            "Apakah kamu punya karya desain, video, atau foto yang pernah dibuat? Ceritakan proses pembuatannya.",
            "Jika membawa portofolio, nilai ide, proses, dan hasil. Jika belum, nilai potensi dan minat.",
        ),
        (
            3,
            "Pemahaman dasar multimedia",
            "Sebutkan software atau aplikasi yang pernah kamu gunakan untuk membuat konten digital.",
            "Contoh: Canva, CapCut, Photoshop, Illustrator, Premiere, dll. Tidak harus mahir semua.",
        ),
        (
            4,
            "Pemahaman dasar multimedia",
            "Menurutmu, apa perbedaan antara resolusi gambar yang bagus dan yang buram?",
            "Cari pemahaman dasar pixel/resolusi/kualitas visual secara sederhana.",
        ),
        (
            5,
            "Kreativitas",
            "Jika diminta membuat poster kegiatan sekolah dalam 1 hari, ide apa yang akan kamu buat?",
            "Nilai kreativitas ide, pemilihan warna/pesan, dan kemampuan menjelaskan konsep.",
        ),
        (
            6,
            "Kreativitas",
            "Ceritakan satu konten digital yang menurutmu menarik, dan mengapa kamu menyukainya.",
            "Lihat kemampuan analisis visual dan rasa estetika.",
        ),
        (
            7,
            "Komunikasi",
            "Bagaimana caramu menjelaskan hasil karyamu kepada orang yang belum paham desain?",
            "Nilai komunikasi sederhana, percaya diri, dan keterbukaan menerima masukan.",
        ),
        (
            8,
            "Motivasi belajar",
            "Apa yang ingin kamu pelajari lebih dalam jika diterima di kelas Multimedia SMARTMU 22?",
            "Pastikan ada tujuan belajar yang konkret dan semangat berkembang.",
        ),
    ],
    "internasional": [
        (
            1,
            "Motivasi kelas internasional",
            "Why do you want to join the International class at SMARTMU 22?",
            "Nilai kemampuan menjawab dalam bahasa Inggris sederhana dan kejelasan motivasi.",
        ),
        (
            2,
            "Kemampuan bahasa Inggris",
            "Please introduce yourself in English (name, hobby, and your dream).",
            "Perhatikan kelancaran speaking, kosakata dasar, dan kepercayaan diri.",
        ),
        (
            3,
            "Kemampuan bahasa Inggris",
            "What do you usually do every day after school? Answer in English.",
            "Nilai kemampuan menyusun kalimat simple present secara alami.",
        ),
        (
            4,
            "Wawasan global",
            "Sebutkan satu negara yang ingin kamu kunjungi dan alasanmu.",
            "Boleh dijawab bilingual. Nilai rasa ingin tahu dan wawasan umum.",
        ),
        (
            5,
            "Wawasan global",
            "Menurutmu, mengapa penting bagi pelajar untuk bisa berbahasa Inggris?",
            "Cari jawaban tentang komunikasi global, pendidikan, dan peluang masa depan.",
        ),
        (
            6,
            "Kemampuan akademik",
            "Mata pelajaran apa yang paling kamu sukai, dan bagaimana caramu belajar di rumah?",
            "Nilai kesiapan akademik dan kebiasaan belajar mandiri.",
        ),
        (
            7,
            "Sikap & kepercayaan diri",
            "If your classmate speaks English better than you, what will you do?",
            "Nilai sikap positif, keberanian berlatih, dan tidak mudah minder.",
        ),
        (
            8,
            "Motivasi kelas internasional",
            "Apa target belajarmu dalam 1 tahun jika masuk kelas Internasional?",
            "Contoh: lebih lancar speaking, berani presentasi, ikut kegiatan berbahasa Inggris.",
        ),
    ],
    "reguler": [
        (
            1,
            "Motivasi sekolah di SMARTMU",
            "Mengapa kamu dan orang tuamu memilih SMP Muhammadiyah 22 Setiabudi Pamulang?",
            "Nilai alasan memilih sekolah, pemahaman nilai Islami, dan kesungguhan mendaftar.",
        ),
        (
            2,
            "Kesiapan akademik",
            "Mata pelajaran apa yang paling kamu kuasai di SD, dan mana yang masih sulit?",
            "Lihat kesadaran diri terhadap kekuatan dan kelemahan belajar.",
        ),
        (
            3,
            "Kesiapan akademik",
            "Bagaimana caramu mengerjakan PR jika ada soal yang belum kamu pahami?",
            "Nilai strategi belajar: baca ulang, tanya guru/orang tua, diskusi teman.",
        ),
        (
            4,
            "Disiplin & tanggung jawab",
            "Ceritakan kebiasaan harianmu: bangun tidur, belajar, membantu orang tua, dan ibadah.",
            "Perhatikan kedisiplinan waktu dan tanggung jawab sederhana.",
        ),
        (
            5,
            "Disiplin & tanggung jawab",
            "Jika kamu terlambat mengumpulkan tugas, apa yang akan kamu lakukan?",
            "Cari kejujuran, tanggung jawab, dan kemauan memperbaiki diri.",
        ),
        (
            6,
            "Dukungan orang tua",
            "Siapa yang biasanya mendampingi belajarmu di rumah, dan bagaimana dukungannya?",
            "Nilai kesiapan keluarga mendampingi proses sekolah.",
        ),
        (
            7,
            "Sikap & komunikasi",
            "Apa yang kamu ketahui tentang sekolah Muhammadiyah dan sikap yang harus dimiliki muridnya?",
            "Nilai pemahaman nilai akhlak, sopan santun, dan semangat belajar.",
        ),
        (
            8,
            "Motivasi sekolah di SMARTMU",
            "Apa komitmenmu jika diterima sebagai murid baru di SMARTMU 22?",
            "Pastikan siap mengikuti tata tertib, belajar sungguh-sungguh, dan menjaga adab.",
        ),
    ],
}

SOAL_CONTOH = {
    "olimpiade": [
        (
            "Hasil dari 15 × 12 − 36 ÷ 6 adalah …",
            "174",
            "168",
            "180",
            "162",
            "A",
        ),
        (
            "Jika 2x + 5 = 17, maka nilai x adalah …",
            "5",
            "6",
            "7",
            "8",
            "B",
        ),
        (
            "Bilangan prima di antara berikut adalah …",
            "21",
            "27",
            "29",
            "33",
            "C",
        ),
    ],
    "tahfidz": [
        (
            "Surah Al-Fatihah terdiri dari berapa ayat?",
            "5",
            "6",
            "7",
            "8",
            "C",
        ),
        (
            "Hukum bacaan nun sukun bertemu ba disebut …",
            "Idgham",
            "Ikhfa",
            "Iqlab",
            "Izhar",
            "C",
        ),
        (
            "Rukun Islam yang pertama adalah …",
            "Shalat",
            "Syahadat",
            "Zakat",
            "Puasa",
            "B",
        ),
    ],
    "multimedia": [
        (
            "Software pengolah gambar berbasis bitmap yang populer adalah …",
            "Adobe Photoshop",
            "Microsoft Word",
            "Notepad",
            "Excel",
            "A",
        ),
        (
            "Resolusi gambar biasanya diukur dalam satuan …",
            "FPS",
            "Pixel",
            "Hz",
            "Watt",
            "B",
        ),
        (
            "Format file video yang umum digunakan adalah …",
            "DOCX",
            "XLSX",
            "MP4",
            "PDF",
            "C",
        ),
    ],
    "internasional": [
        (
            "What is the capital city of England?",
            "Paris",
            "London",
            "Berlin",
            "Rome",
            "B",
        ),
        (
            "Choose the correct sentence:",
            "She go to school every day.",
            "She goes to school every day.",
            "She going to school every day.",
            "She gone to school every day.",
            "B",
        ),
        (
            "Synonym of 'happy' is …",
            "Sad",
            "Angry",
            "Joyful",
            "Tired",
            "C",
        ),
    ],
    "reguler": [
        (
            "Ibu kota Negara Kesatuan Republik Indonesia adalah …",
            "Surabaya",
            "Bandung",
            "Jakarta",
            "Medan",
            "C",
        ),
        (
            "Hasil dari 8 × 7 adalah …",
            "54",
            "56",
            "63",
            "49",
            "B",
        ),
        (
            "Hewan yang berkembang biak dengan bertelur disebut …",
            "Vivipar",
            "Ovipar",
            "Ovovivipar",
            "Metamorfosis",
            "B",
        ),
    ],
}


def seed_initial_data():
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            nama_lengkap="Administrator TPK",
            email="admin@smartmu22.sch.id",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)

    guru_seed = [
        ("guru_olimpiade", "Guru Penguji Olimpiade", "olimpiade", "guru.olimpiade@smartmu22.sch.id"),
        ("guru_tahfidz", "Guru Penguji Tahfidz", "tahfidz", "guru.tahfidz@smartmu22.sch.id"),
        ("guru_multimedia", "Guru Penguji Multimedia", "multimedia", "guru.multimedia@smartmu22.sch.id"),
        ("guru_internasional", "Guru Penguji Internasional", "internasional", "guru.internasional@smartmu22.sch.id"),
        ("guru_reguler", "Guru Penguji Reguler", "reguler", "guru.reguler@smartmu22.sch.id"),
    ]
    for username, nama, kelas, email in guru_seed:
        if not User.query.filter_by(username=username).first():
            guru = User(
                username=username,
                nama_lengkap=nama,
                email=email,
                role="guru",
                kelas_penguji=kelas,
            )
            guru.set_password("guru123")
            db.session.add(guru)

    # Guru pembuat soal: hanya akses bank soal kelas yang ditugaskan
    guru_soal_seed = [
        ("soal_olimpiade", "Pembuat Soal Olimpiade", "olimpiade", "soal.olimpiade@smartmu22.sch.id"),
        ("soal_tahfidz", "Pembuat Soal Tahfidz", "tahfidz", "soal.tahfidz@smartmu22.sch.id"),
        ("soal_multimedia", "Pembuat Soal Multimedia", "multimedia", "soal.multimedia@smartmu22.sch.id"),
        ("soal_internasional", "Pembuat Soal Internasional", "internasional", "soal.internasional@smartmu22.sch.id"),
        ("soal_reguler", "Pembuat Soal Reguler", "reguler", "soal.reguler@smartmu22.sch.id"),
    ]
    for username, nama, kelas, email in guru_soal_seed:
        if not User.query.filter_by(username=username).first():
            gs = User(
                username=username,
                nama_lengkap=nama,
                email=email,
                role="guru_soal",
                kelas_penguji=kelas,
            )
            gs.set_password("guru123")
            db.session.add(gs)

    if KriteriaPenilaian.query.count() == 0:
        for kelas, items in KRITERIA_DEFAULT.items():
            for nama, deskripsi, bobot in items:
                db.session.add(
                    KriteriaPenilaian(
                        kelas_tujuan=kelas,
                        nama_kriteria=nama,
                        deskripsi=deskripsi,
                        bobot=bobot,
                        skor_maks=bobot,
                    )
                )
    else:
        # Samakan skor_maks dengan bobot agar total kelas = 100
        for item in KriteriaPenilaian.query.all():
            if item.skor_maks != item.bobot:
                item.skor_maks = item.bobot

    if SoalTes.query.count() == 0:
        for kelas, soals in SOAL_CONTOH.items():
            for pertanyaan, a, b, c, d, benar in soals:
                db.session.add(
                    SoalTes(
                        kelas_tujuan=kelas,
                        pertanyaan=pertanyaan,
                        opsi_a=a,
                        opsi_b=b,
                        opsi_c=c,
                        opsi_d=d,
                        jawaban_benar=benar,
                    )
                )

    # Bobot 8 soal = 100 poin per kelas
    BOBOT_SOAL = [13, 12, 13, 12, 13, 12, 13, 12]

    if SoalWawancara.query.count() == 0:
        for kelas, items in SOAL_WAWANCARA.items():
            for idx, (urutan, aspek, pertanyaan, panduan) in enumerate(items):
                bobot = BOBOT_SOAL[idx] if idx < len(BOBOT_SOAL) else 12
                db.session.add(
                    SoalWawancara(
                        kelas_tujuan=kelas,
                        aspek=aspek,
                        pertanyaan=pertanyaan,
                        panduan=panduan,
                        bobot=bobot,
                        urutan=urutan,
                        is_active=True,
                    )
                )
    else:
        # Pastikan bobot terisi & total mendekati 100 per kelas
        from collections import defaultdict

        by_kelas = defaultdict(list)
        for soal in SoalWawancara.query.filter_by(is_active=True).order_by(
            SoalWawancara.urutan, SoalWawancara.id
        ).all():
            by_kelas[soal.kelas_tujuan].append(soal)
        for _kelas, soals in by_kelas.items():
            if all((s.bobot or 0) > 0 for s in soals) and sum(s.bobot or 0 for s in soals) == 100:
                continue
            n = len(soals)
            if n == 0:
                continue
            base = 100 // n
            sisa = 100 - (base * n)
            for i, soal in enumerate(soals):
                soal.bobot = base + (1 if i < sisa else 0)

    defaults = [
        ("nama_sekolah", "SMP Muhammadiyah 22 Setiabudi Pamulang", "Nama sekolah"),
        ("nama_aplikasi", "TPK SMARTMU22", "Nama aplikasi"),
        ("tahun_ajaran", "2026/2027", "Tahun ajaran aktif"),
        ("gelombang_aktif", "1", "Gelombang tes penempatan yang sedang berjalan"),
        ("daftar_gelombang", "1,2,3", "Daftar gelombang dalam satu tahun ajaran"),
        ("bobot_tes_tertulis", "30", "Persentase bobot tes tertulis (default)"),
        ("bobot_wawancara", "50", "Persentase bobot wawancara (default)"),
        ("bobot_psikotes", "20", "Persentase bobot psikotes (default)"),
        ("batas_lulus", "70", "Nilai minimal kelulusan penempatan"),
        ("tampilkan_kisi_kisi", "1", "Tampilkan kisi-kisi soal ke ortu & murid"),
    ]
    for kunci, nilai, ket in defaults:
        if not Pengaturan.query.filter_by(kunci=kunci).first():
            db.session.add(Pengaturan(kunci=kunci, nilai=nilai, keterangan=ket))

    # Bobot & kuota awal per kelas (bisa diubah admin di Pengaturan)
    from tpk.models import KELAS_CHOICES

    for kode, label in KELAS_CHOICES:
        for kunci, nilai, ket in (
            (f"bobot_tes_{kode}", "30", f"Bobot tes tertulis kelas {label}"),
            (f"bobot_wawancara_{kode}", "50", f"Bobot wawancara kelas {label}"),
            (f"bobot_psikotes_{kode}", "20", f"Bobot psikotes kelas {label}"),
            (f"kuota_{kode}", "0", f"Kuota penempatan kelas {label} (0=tidak dibatasi)"),
        ):
            if not Pengaturan.query.filter_by(kunci=kunci).first():
                db.session.add(Pengaturan(kunci=kunci, nilai=nilai, keterangan=ket))

    db.session.commit()