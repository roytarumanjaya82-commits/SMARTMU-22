import {
  BIDANG,
  OLAH,
  PENGALAMAN,
  PREDIKAT,
  PRINSIP,
  PROFIL,
  esc,
  formatTanggalID,
  kelasIdPada,
  layananUntukSiswa,
  lihatRaport,
  namaPredikat,
  ringkasPengalaman,
  ringkasPrinsip,
  siswaDiKelas,
  usulanCatatanGuru,
} from "./model.js?v=13";

function garis(teks) {
  const isi = String(teks || "").trim();
  if (!isi) return '<span class="kosong">—</span>';
  return esc(isi).replace(/\n/g, "<br>");
}

function cap(kode) {
  if (!kode) return '<span class="kosong">—</span>';
  return `<span class="cap ${esc(kode)}">${esc(kode)}</span> ${esc(namaPredikat(kode))}`;
}

function kop(sekolah) {
  return `<header class="kop">
    <div class="kop-baris">
      <img class="logo-sekolah" src="img/logo-smpm22.png" alt="Logo SMP Muhammadiyah 22 Setiabudi Pamulang">
      <div class="kop-teks">
        <div class="yayasan">${esc(sekolah.yayasan || "Persyarikatan Muhammadiyah")}</div>
        <h1>${esc(sekolah.nama)}</h1>
        <p class="npsn">NPSN ${esc(sekolah.npsn)}</p>
        <p>${esc(sekolah.alamat)}</p>
        <p>Telp. ${esc(sekolah.telepon)} · ${esc(sekolah.email)}</p>
      </div>
    </div>
  </header>`;
}

function judul(periode, sub) {
  return `<div class="judul-raport">
    <h2>Laporan Perkembangan Bimbingan dan Konseling</h2>
    <p>Kurikulum Merdeka · Pendekatan Pembelajaran Mendalam · Fase ${esc(sub.fase || "D")}</p>
    <p class="periode">Tahun Ajaran ${esc(periode.tahunAjaran)} · Semester ${esc(periode.semester)}</p>
  </div>`;
}

function ttd(peranHtml, nama, nbm) {
  return `<div class="ttd">
    <div class="ttd-peran">${peranHtml}</div>
    <div class="ttd-ruang"></div>
    <div class="ttd-nama">${nama ? esc(nama) : "............................"}</div>
    ${nbm ? `<div class="ttd-nbm">NBM : ${esc(nbm)}</div>` : ""}
  </div>`;
}

function blokTtd(sekolah, guru, waliNama, waliNbm, kota, tanggal) {
  return `<div class="ttd-wrap keep">
    <div class="ttd-tanggal">${esc(kota || "Pamulang")}, ${esc(formatTanggalID(tanggal))}</div>
    <div class="ttd-grid">
      ${ttd("Orang Tua / Wali", "", "")}
      ${ttd("Wali Kelas", waliNama, waliNbm)}
      ${ttd("Mengetahui,<br>Kepala Sekolah", sekolah.kepalaSekolah, sekolah.nipKepalaSekolah)}
      ${ttd(esc(guru.jabatan || "Guru Bimbingan dan Konseling"), guru.nama, guru.nip)}
    </div>
  </div>
  <p class="catatan-kaki">Laporan ini menggambarkan perkembangan murid, bukan nilai akademik. Catatan konseling yang bersifat pribadi tidak dicantumkan dan tetap menjadi arsip rahasia guru BK.</p>`;
}

export function htmlRaportSiswa(state, siswa, { tanggal, kelas } = {}) {
  const sekolah = state.sekolah;
  const guru = state.guru;
  const periode = state.periode;
  const rec = lihatRaport(state, siswa.id);
  const layanan = layananUntukSiswa(state, siswa.id);
  const prinsipOtomatis = ringkasPrinsip(layanan);
  const pengalamanOtomatis = ringkasPengalaman(layanan);
  const catatanOtomatis = usulanCatatanGuru(state, siswa.id);
  const rahasia = layanan.filter((l) => l.rahasia).length;
  const terbuka = layanan.filter((l) => !l.rahasia);
  const kelasNama = kelas?.nama || rec.snapshot?.kelas || "";
  const ttl = [siswa.tempatLahir, siswa.tanggalLahir ? formatTanggalID(siswa.tanggalLahir) : ""].filter(Boolean).join(", ");
  const jk = siswa.jk === "L" ? "Laki-laki" : siswa.jk === "P" ? "Perempuan" : "—";

  const bidangRows = BIDANG.map((b) => {
    const item = rec.bidang[b.id];
    return `<tr>
      <td class="bidang">${esc(b.nama)}</td>
      <td class="capaian">${cap(item.predikat)}</td>
      <td>${garis(item.deskripsi)}</td>
    </tr>`;
  }).join("");

  const profilRows = PROFIL.map((p) => {
    const item = rec.profil[p.id];
    return `<tr>
      <td>${esc(p.nama)}</td>
      <td class="capaian">${cap(item.capaian)}</td>
      <td>${garis(item.deskripsi)}</td>
    </tr>`;
  }).join("");

  const prinsipRows = PRINSIP.map((p) => `<tr><td>${esc(p.nama)}</td><td>${garis(rec.prinsipCatatan[p.id] || prinsipOtomatis[p.id])}</td></tr>`).join("");
  const pengalamanRows = PENGALAMAN.map((p) => `<tr><td>${esc(p.nama)}</td><td>${garis(rec.pengalamanCatatan[p.id] || pengalamanOtomatis[p.id])}</td></tr>`).join("");
  const olahAda = OLAH.some((o) => String(rec.olah[o.id] || "").trim());
  const olahRows = OLAH.map((o) => `<tr><td>${esc(o.nama)}</td><td>${garis(rec.olah[o.id])}</td></tr>`).join("");

  const layananRows = terbuka.length
    ? terbuka
        .map((l) => `<tr>
          <td>${esc(formatTanggalID(l.tanggal))}</td>
          <td>${esc(l.jenis)}</td>
          <td>${esc(l.bidang || "")}</td>
          <td>${esc(l.topik)}</td>
        </tr>`)
        .join("")
    : `<tr><td colspan="4">Belum ada layanan terbuka yang tercatat pada semester ini.</td></tr>`;

  const kh = rec.kehadiran || {};
  return `<article class="sheet">
    ${kop(sekolah)}
    ${judul(periode, sekolah)}
    <h3>A. Identitas Murid</h3>
    <table class="identitas">
      <tr><th>Nama</th><td>${esc(siswa.nama)}</td><th>NISN</th><td>${esc(siswa.nisn || "—")}</td></tr>
      <tr><th>Kelas</th><td>${esc(kelasNama || "—")}</td><th>NIS</th><td>${esc(siswa.nis || "—")}</td></tr>
      <tr><th>Jenis kelamin</th><td>${jk}</td><th>Nomor absen</th><td>${esc(siswa.noAbsen || "—")}</td></tr>
      <tr><th>Tempat, tanggal lahir</th><td>${esc(ttl || "—")}</td><th>Agama</th><td>${esc(siswa.agama || "—")}</td></tr>
      <tr><th>Nama ayah</th><td>${esc(siswa.namaAyah || "—")}</td><th>Nama ibu</th><td>${esc(siswa.namaIbu || "—")}</td></tr>
    </table>

    <h3>B. Perkembangan Bidang Layanan</h3>
    <table class="kisi">
      <thead><tr><th>Bidang</th><th>Capaian</th><th>Uraian perkembangan</th></tr></thead>
      <tbody>${bidangRows}</tbody>
    </table>
    <p class="legenda">SB Sangat Berkembang · BSH Berkembang Sesuai Harapan · MB Mulai Berkembang · BB Belum Berkembang. Kehadiran layanan: Hadir ${esc(kh.hadir || "—")}, Sakit ${esc(kh.sakit || "—")}, Izin ${esc(kh.izin || "—")}, Alfa ${esc(kh.alfa || "—")}.</p>

    <h3>C. Dimensi Profil Lulusan</h3>
    <p class="pengantar">Delapan dimensi profil lulusan pada pendekatan Pembelajaran Mendalam, dikuatkan melalui layanan bimbingan dan konseling.</p>
    <table class="kisi">
      <thead><tr><th>Dimensi</th><th>Capaian</th><th>Uraian</th></tr></thead>
      <tbody>${profilRows}</tbody>
    </table>

    <h3>D. Pembelajaran Mendalam</h3>
    <p class="pengantar">Prinsip berkesadaran, bermakna, dan menggembirakan melalui pengalaman memahami, mengaplikasi, dan merefleksi.</p>
    <div class="dua-kolom">
      <table class="kisi">
        <thead><tr><th>Prinsip</th><th>Catatan</th></tr></thead>
        <tbody>${prinsipRows}</tbody>
      </table>
      <table class="kisi">
        <thead><tr><th>Pengalaman belajar</th><th>Catatan</th></tr></thead>
        <tbody>${pengalamanRows}</tbody>
      </table>
    </div>
    ${olahAda ? `<table class="kisi"><thead><tr><th>Olah utuh</th><th>Catatan</th></tr></thead><tbody>${olahRows}</tbody></table>` : ""}

    <h3>E. Partisipasi Layanan BK</h3>
    <table class="kisi">
      <thead><tr><th>Tanggal</th><th>Jenis</th><th>Bidang</th><th>Topik</th></tr></thead>
      <tbody>${layananRows}</tbody>
    </table>
    ${rahasia ? `<p class="pengantar">Layanan individual yang bersifat rahasia tercatat ${rahasia} kali dan tidak diuraikan pada laporan ini.</p>` : ""}

    <h3>F. Catatan Guru BK dan Tindak Lanjut</h3>
    <table class="kisi catatan">
      <tr><th>Kekuatan</th><td>${garis(rec.kekuatan || catatanOtomatis.kekuatan)}</td></tr>
      <tr><th>Perlu pendampingan</th><td>${garis(rec.pendampingan || catatanOtomatis.pendampingan)}</td></tr>
      <tr><th>Catatan perkembangan</th><td>${garis(rec.catatanGuru || catatanOtomatis.catatanGuru)}</td></tr>
      <tr><th>Rekomendasi bagi orang tua</th><td>${garis(rec.rekomendasiOrangtua || catatanOtomatis.rekomendasiOrangtua)}</td></tr>
      <tr><th>Tindak lanjut</th><td>${garis(rec.tindakLanjut || catatanOtomatis.tindakLanjut)}</td></tr>
    </table>
    ${blokTtd(sekolah, guru, kelas?.waliKelas || "", kelas?.nbmWali || "", sekolah.kota, tanggal)}
  </article>`;
}

export function htmlRekapKelas(state, kelas, { tanggal } = {}) {
  const siswa = siswaDiKelas(state, kelas.id);
  const layananKelas = state.layanan.filter((l) => {
    return l.tahunAjaran === state.periode.tahunAjaran && l.semester === state.periode.semester && l.kelasId === kelas.id && !l.rahasia;
  });
  const body = siswa.length
    ? siswa
        .map((s, i) => {
          const rec = lihatRaport(state, s.id);
          const ket = rec.kekuatan || rec.catatanGuru || "";
          const sel = (id) => {
            const kode = rec.bidang[id].predikat;
            return `<td class="tengah ${kode ? `cap ${kode}` : ""}">${esc(kode || "—")}</td>`;
          };
          return `<tr>
            <td class="tengah">${i + 1}</td>
            <td>${esc(s.nama)}</td>
            <td>${esc(s.nisn || "—")}</td>
            <td class="tengah">${esc(s.jk || "—")}</td>
            ${sel("pribadi")}${sel("sosial")}${sel("belajar")}${sel("karir")}
            <td>${esc(ket.length > 90 ? `${ket.slice(0, 90)}…` : ket) || '<span class="kosong">—</span>'}</td>
          </tr>`;
        })
        .join("")
    : `<tr><td colspan="9">Belum ada murid di kelas ini.</td></tr>`;

  const hitung = { SB: 0, BSH: 0, MB: 0, BB: 0, kosong: 0 };
  for (const s of siswa) {
    const rec = lihatRaport(state, s.id);
    for (const b of BIDANG) {
      const kode = rec.bidang[b.id].predikat;
      if (hitung[kode] != null) hitung[kode]++;
      else hitung.kosong++;
    }
  }
  const topik = [];
  for (const l of layananKelas) if (l.topik && !topik.includes(l.topik)) topik.push(`${l.jenis}: ${l.topik}`);

  return `<article class="sheet">
    ${kop(state.sekolah)}
    ${judul(state.periode, state.sekolah)}
    <h3>Rekapitulasi Kelas ${esc(kelas.nama)}</h3>
    <p class="pengantar">Wali kelas: ${esc(kelas.waliKelas || "—")} · ${siswa.length} murid. Rekap ini untuk arsip guru BK dan wali kelas. Uraian lengkap tercetak pada laporan masing-masing murid.</p>
    <table class="kisi rekap">
      <thead>
        <tr>
          <th>No</th><th>Nama</th><th>NISN</th><th>L/P</th>
          <th>Pribadi</th><th>Sosial</th><th>Belajar</th><th>Karir</th><th>Catatan singkat</th>
        </tr>
      </thead>
      <tbody>${body}</tbody>
    </table>
    <p class="legenda">Jumlah isian bidang: SB ${hitung.SB} · BSH ${hitung.BSH} · MB ${hitung.MB} · BB ${hitung.BB} · belum diisi ${hitung.kosong}.</p>
    <h3>Layanan kelas pada semester ini</h3>
    <p class="pengantar">${topik.length ? esc(topik.join("; ")) : "Belum ada layanan kelas yang tercatat."}</p>
    ${blokTtd(state.sekolah, state.guru, kelas.waliKelas, kelas.nbmWali || "", state.sekolah.kota, tanggal)}
  </article>`;
}

export function htmlCetak(state, opts) {
  const tanggal = opts.tanggal || new Date().toISOString().slice(0, 10);
  if (opts.mode === "kelas") {
    const kelas = state.kelas.find((k) => k.id === opts.kelasId);
    if (!kelas) return `<article class="sheet"><p>Kelas belum dipilih.</p></article>`;
    let html = htmlRekapKelas(state, kelas, { tanggal });
    if (opts.lengkap) {
      for (const siswa of siswaDiKelas(state, kelas.id)) html += htmlRaportSiswa(state, siswa, { tanggal, kelas });
    }
    return html;
  }
  const siswa = state.siswa.find((s) => s.id === opts.siswaId);
  if (!siswa) return `<article class="sheet"><p>Murid belum dipilih.</p></article>`;
  const kelas = state.kelas.find((k) => k.id === kelasIdPada(state, siswa));
  return htmlRaportSiswa(state, siswa, { tanggal, kelas });
}
