import {
  BIDANG,
  INDIKATOR,
  JENIS_LAYANAN,
  OLAH,
  PENGALAMAN,
  PREDIKAT,
  PRINSIP,
  PROFIL,
  bandingKelas,
  esc,
  kelasIdPada,
  lihatRaport,
  namaPredikat,
  raportTerisiPredikat,
  siswaDiKelas,
  statistik,
} from "./model.js?v=13";
import { htmlCetak } from "./print.js?v=13";
import { getClientId as clientTersimpan, status } from "./store.js?v=13";

const NAV = [
  ["beranda", "Beranda"],
  ["murid", "Daftar Murid"],
  ["raport", "Isi Raport"],
  ["layanan", "Layanan BK"],
  ["cetak", "Cetak"],
  ["pengaturan", "Pengaturan"],
  ["panduan", "Panduan"],
];

function tahunInput(state) {
  return `<label>Tahun ajaran
      <input data-bind="periode.tahunAjaran" data-render="1" value="${esc(state.periode.tahunAjaran)}" autocomplete="off">
    </label>
    <label>Semester
      <select data-bind="periode.semester" data-render="1">
        <option ${state.periode.semester === "Ganjil" ? "selected" : ""}>Ganjil</option>
        <option ${state.periode.semester === "Genap" ? "selected" : ""}>Genap</option>
      </select>
    </label>`;
}

function aside(state, route) {
  return `<aside class="screen-only">
    <div class="brand">
      <img class="mark" src="img/logo-smpm22.png" alt="Logo SMP Muhammadiyah 22 Setiabudi Pamulang">
      <div><strong>Raport BK</strong><span>SMP Muhammadiyah 22<br>Setiabudi Pamulang</span></div>
      <button type="button" class="garis-hp" data-menu-hp aria-label="Buka menu"><span></span><span></span><span></span></button>
    </div>
    <nav>
      ${NAV.map(([id, nama]) => `<a href="#/${id}" class="${route === id ? "aktif" : ""}">${nama}</a>`).join("")}
    </nav>
    <div class="aside-foot">
      ${tahunInput(state)}
      <div>${esc(state.guru.nama || "Nama guru belum diisi")}</div>
    </div>
  </aside>`;
}

function kepala(judul, lead, ekstra = "") {
  return `<div class="page-head"><div><h1>${judul}</h1><p class="lead">${lead}</p></div>${ekstra}</div>`;
}

function opsiKelas(state, terpilih) {
  return state.kelas
    .slice()
    .sort(bandingKelas)
    .map((k) => `<option value="${esc(k.id)}" ${k.id === terpilih ? "selected" : ""}>${esc(k.nama)}</option>`)
    .join("");
}

function chips(state, ui) {
  if (!state.kelas.length) return `<p class="muted">Belum ada kelas. Unggah daftar murid atau tambah kelas.</p>`;
  return `<div class="chips">${state.kelas
    .slice()
    .sort(bandingKelas)
    .map((k) => {
      const n = siswaDiKelas(state, k.id).length;
      return `<button type="button" class="chip ${k.id === ui.kelasId ? "on" : ""}" data-act="pilih-kelas" data-id="${esc(k.id)}">${esc(k.nama)} <span>${n}</span></button>`;
    })
    .join("")}</div>`;
}

function pratinjauImpor(preview) {
  if (!preview) return "";
  const grup = {};
  for (const s of preview.siswa) (grup[s.kelas] ||= []).push(s);
  const kelas = Object.keys(grup).sort();
  const daftar = kelas
    .map((k) => {
      const contoh = grup[k]
        .slice(0, 4)
        .map((s) => esc(s.nama))
        .join(", ");
      return `<li><strong>${esc(k)}</strong> — ${grup[k].length} murid. ${contoh}${grup[k].length > 4 ? ", dan lainnya" : ""}</li>`;
    })
    .join("");
  const gagal = preview.errors.slice(0, 8).map((e) => `<li>${esc(e)}</li>`).join("");
  return `<div class="panel" style="margin-bottom:14px">
    <h2>Pratinjau ${esc(preview.fileName)}</h2>
    <p>Daftar murid yang sekarang akan dihapus, lalu diganti dengan ${preview.siswa.length} murid dari berkas ini. Raport murid lama ikut terhapus. Nama wali kelas yang sama tetap dipakai.</p>
    <ul>${daftar || "<li>Tidak ada murid yang siap dimasukkan.</li>"}</ul>
    ${gagal ? `<p class="kecil">Baris yang dilewati:</p><ul class="kecil">${gagal}</ul>` : ""}
    <div class="aksi">
      <button type="button" class="btn btn-primary" data-act="impor-ya" ${preview.siswa.length ? "" : "disabled"}>Ganti daftar murid</button>
      <button type="button" class="btn" data-act="impor-batal">Batalkan</button>
    </div>
  </div>`;
}

function angkaRingkas(state) {
  const st = statistik(state);
  const persen = st.siswa ? Math.round((st.isi / st.siswa) * 100) : 0;
  return `<div class="stats">
      <div class="stat"><b>${st.kelas}</b>Kelas aktif</div>
      <div class="stat"><b>${st.siswa}</b>Murid ${esc(state.periode.tahunAjaran)}</div>
      <div class="stat"><b>${st.isi}</b>Raport berpredikat<div class="bar"><span style="width:${persen}%"></span></div></div>
      <div class="stat"><b>${st.layanan}</b>Layanan semester ini</div>
    </div>`;
}

function beranda(state) {
  const layanan = state.layanan
    .filter((l) => l.tahunAjaran === state.periode.tahunAjaran && l.semester === state.periode.semester)
    .slice(0, 5);
  const folder = status.folder === "saved" ? `Folder tersambung: ${esc(status.folderName)}` : "Folder Google Drive belum disambungkan.";
  const akun = status.googleEmail ? esc(status.googleEmail) : "Belum masuk akun Google pada sesi ini.";
  return `${kepala("Raport Bimbingan dan Konseling", "Pengolahan raport BK SMP Muhammadiyah 22 Setiabudi Pamulang, Kurikulum Merdeka dengan pendekatan Pembelajaran Mendalam. Data tetap tersimpan di komputer saat internet mati.")}
    ${state.siswa.length ? "" : `<div class="banner">Mulai dari tiga langkah: lengkapi nama guru, unggah daftar murid sesuai kelas, lalu sambungkan folder Google Drive akun guru.</div>`}
    ${angkaRingkas(state)}
    <div class="grid-2">
      <div class="card">
        <h2>Langkah kerja</h2>
        <div class="steps">
          <div class="step"><div class="num">1</div><div><strong>Identitas guru dan kepala sekolah</strong><p class="kecil">Diisi sekali di menu Pengaturan. Nama guru tercetak pada raport.</p></div></div>
          <div class="step"><div class="num">2</div><div><strong>Unggah daftar murid per kelas</strong><p class="kecil">Berkas Excel atau CSV. Satu berkas boleh berisi banyak kelas, atau satu lembar per kelas.</p><a href="#/murid">Buka daftar murid</a></div></div>
          <div class="step"><div class="num">3</div><div><strong>Isi perkembangan dan cetak</strong><p class="kecil">Predikat empat bidang layanan, dimensi profil lulusan, lalu cetak per siswa atau per kelas.</p></div></div>
        </div>
      </div>
      <div class="card">
        <h2>Penyimpanan Google Drive</h2>
        <p>${folder}</p>
        <p class="kecil">Akun: ${akun}</p>
        <div class="aksi">
          <button type="button" class="btn btn-primary" data-act="sambung-folder">Sambungkan folder Google Drive</button>
          ${status.folder === "needs-permission" ? `<button type="button" class="btn" data-act="izin-folder">Izinkan folder lagi</button>` : ""}
          <button type="button" class="btn" data-act="masuk-google">Masuk akun Google</button>
        </div>
        <p class="kecil">Folder dipakai bersama aplikasi Google Drive di komputer, jadi tetap bisa diisi saat offline. Masuk akun Google menulis langsung ke Drive awan dan membutuhkan Client ID di Pengaturan.</p>
        ${status.folderError ? `<p class="kecil">${esc(status.folderError)}</p>` : ""}
        ${status.googleError ? `<p class="kecil">${esc(status.googleError)}</p>` : ""}
      </div>
    </div>
    <div class="card" style="margin-top:14px">
      <h2>Layanan terakhir semester ini</h2>
      ${layanan.length ? `<ul>${layanan.map((l) => `<li>${esc(l.tanggal)} — ${esc(l.jenis)}: ${esc(l.topik)}${l.rahasia ? " (rahasia)" : ""}</li>`).join("")}</ul>` : `<p class="muted">Belum ada layanan pada ${esc(state.periode.semester)} ${esc(state.periode.tahunAjaran)}.</p>`}
    </div>`;
}

function murid(state, ui) {
  const kelas = state.kelas.find((k) => k.id === ui.kelasId);
  const daftar = kelas ? siswaDiKelas(state, kelas.id) : [];
  const baris = daftar
    .map((s, i) => {
      const cari = esc(`${s.nama} ${s.nisn} ${s.nis}`.toLowerCase());
      const buka = ui.detailId === s.id;
      return `<tr data-cari="${cari}">
        <td>${i + 1}</td>
        <td><input data-siswa="${esc(s.id)}" data-field="nama" value="${esc(s.nama)}" autocomplete="off"></td>
        <td><input data-siswa="${esc(s.id)}" data-field="nisn" value="${esc(s.nisn)}" autocomplete="off"></td>
        <td><select data-siswa="${esc(s.id)}" data-field="jk"><option value=""></option><option value="L" ${s.jk === "L" ? "selected" : ""}>L</option><option value="P" ${s.jk === "P" ? "selected" : ""}>P</option></select></td>
        <td><input data-siswa="${esc(s.id)}" data-field="noAbsen" value="${esc(s.noAbsen)}" autocomplete="off"></td>
        <td><select data-siswa="${esc(s.id)}" data-field="kelasId">${opsiKelas(state, kelasIdPada(state, s))}</select></td>
        <td class="aksi">
          <button type="button" class="btn btn-kecil" data-act="detail-siswa" data-id="${esc(s.id)}">${buka ? "Tutup" : "Detail"}</button>
          <button type="button" class="btn btn-kecil" data-act="cetak-siswa" data-id="${esc(s.id)}">Cetak</button>
          <button type="button" class="btn btn-kecil btn-danger" data-act="hapus-siswa" data-id="${esc(s.id)}">Hapus</button>
        </td>
      </tr>
      ${buka ? `<tr data-cari="${cari}"><td colspan="7">
        <div class="dua">
          <label class="field"><span>NIS</span><input data-siswa="${esc(s.id)}" data-field="nis" value="${esc(s.nis)}"></label>
          <label class="field"><span>Agama</span><input data-siswa="${esc(s.id)}" data-field="agama" value="${esc(s.agama)}"></label>
          <label class="field"><span>Tempat lahir</span><input data-siswa="${esc(s.id)}" data-field="tempatLahir" value="${esc(s.tempatLahir)}"></label>
          <label class="field"><span>Tanggal lahir</span><input type="date" data-siswa="${esc(s.id)}" data-field="tanggalLahir" value="${esc(s.tanggalLahir)}"></label>
          <label class="field"><span>Nama ayah</span><input data-siswa="${esc(s.id)}" data-field="namaAyah" value="${esc(s.namaAyah)}"></label>
          <label class="field"><span>Nama ibu</span><input data-siswa="${esc(s.id)}" data-field="namaIbu" value="${esc(s.namaIbu)}"></label>
        </div>
      </td></tr>` : ""}`;
    })
    .join("");
  return `${kepala("Daftar murid", "Unggah berkas sesuai kelas, atau tambah murid satu per satu. Penempatan mengikuti tahun ajaran yang sedang dipilih di sisi kiri.", `<div class="aksi"><button type="button" class="btn btn-gold" data-act="unduh-template">Unduh template Excel</button></div>`)}
    ${angkaRingkas(state)}
    ${pratinjauImpor(ui.preview)}
    <div class="zona" id="zona-impor">
      <strong>Letakkan berkas Excel atau CSV di sini</strong>
      <p class="kecil">Kolom yang dibaca: Nama, Kelas, NISN, NIS, Jenis Kelamin, No Absen, Tempat Lahir, Tanggal Lahir, Agama, Nama Ayah, Nama Ibu. Jika kolom Kelas kosong, nama lembar Excel dipakai sebagai nama kelas.</p>
      <button type="button" class="btn btn-primary" data-act="pilih-berkas">Pilih berkas</button>
      <input id="berkas-murid" class="sr" type="file" accept=".csv,.txt,.xlsx,.xls">
    </div>
    <div class="aksi" style="margin-top:12px">
      <button type="button" class="btn" data-act="buka-kelas">${ui.showKelasForm ? "Tutup form kelas" : "Tambah kelas"}</button>
      ${kelas ? `<button type="button" class="btn" data-act="rapikan-nama">Rapikan huruf nama kelas ini</button>` : ""}
      ${kelas ? `<button type="button" class="btn btn-danger" data-act="hapus-kelas" data-id="${esc(kelas.id)}">Hapus kelas ${esc(kelas.nama)}</button>` : ""}
    </div>
    ${ui.showKelasForm ? `<div class="panel" style="margin-top:10px"><div class="dua">
      <label class="field"><span>Nama kelas, misalnya 7A</span><input id="kelas-baru" autocomplete="off"></label>
      <label class="field"><span>Wali kelas</span><input id="wali-baru" autocomplete="off"></label>
    </div><button type="button" class="btn btn-primary" data-act="simpan-kelas">Simpan kelas</button></div>` : ""}
    ${chips(state, ui)}
    ${kelas ? `<div class="dua"><label class="field"><span>Wali kelas ${esc(kelas.nama)}</span><input data-kelas="${esc(kelas.id)}" data-field="waliKelas" value="${esc(kelas.waliKelas || "")}" autocomplete="off"></label>
      <label class="field"><span>NBM wali kelas</span><input data-kelas="${esc(kelas.id)}" data-field="nbmWali" value="${esc(kelas.nbmWali || "")}" autocomplete="off" placeholder="NBM : ........."></label></div>
    <div class="tiga">
      <label class="field"><span>Nama murid baru</span><input id="baru-nama" autocomplete="off"></label>
      <label class="field"><span>L/P</span><select id="baru-jk"><option value="L">L</option><option value="P">P</option></select></label>
      <label class="field"><span>NISN</span><input id="baru-nisn" autocomplete="off"></label>
      <button type="button" class="btn btn-primary" data-act="tambah-siswa">Tambah</button>
    </div>
    <label class="field"><span>Cari di kelas ini</span><input id="cari-murid" placeholder="Nama atau NISN" autocomplete="off"></label>
    <table class="data" id="tabel-murid">
      <thead><tr><th>No</th><th>Nama</th><th>NISN</th><th>JK</th><th>Absen</th><th>Kelas</th><th></th></tr></thead>
      <tbody>${baris || `<tr><td colspan="7">Kelas ini belum memiliki murid pada tahun ajaran ini.</td></tr>`}</tbody>
    </table>` : ""}`;
}

function seg(siswaId, bidang, sekarang) {
  return `<div class="seg">${PREDIKAT.map((p) => `<button type="button" class="seg-btn p-${p.id} ${sekarang === p.id ? "on" : ""}" data-act="predikat" data-siswa="${esc(siswaId)}" data-bidang="${bidang}" data-nilai="${p.id}">${p.id}</button>`).join("")}
    <button type="button" class="btn btn-kecil" data-act="kosong-predikat" data-siswa="${esc(siswaId)}" data-bidang="${bidang}">Kosongkan</button></div>
    <span class="kecil pred-nama">${esc(namaPredikat(sekarang) || "Belum dipilih")}</span>`;
}

function raport(state, ui) {
  const kelas = state.kelas.find((k) => k.id === ui.kelasId);
  const daftar = kelas ? siswaDiKelas(state, kelas.id) : [];
  const siswa = daftar.find((s) => s.id === ui.siswaId) || daftar[0];
  const tabSiswa = ui.tabRaport !== "cepat";
  const daftarHtml = daftar
    .map((s) => {
      const lengkap = raportTerisiPredikat(lihatRaport(state, s.id));
      return `<button type="button" class="siswa-item ${siswa && s.id === siswa.id ? "on" : ""}" data-act="pilih-siswa" data-id="${esc(s.id)}">
        <i class="dot ${lengkap ? "done" : ""}" data-dot="${esc(s.id)}"></i>
        <span><strong>${esc(s.nama)}</strong><small>${esc(s.nisn || "NISN belum diisi")}</small></span>
      </button>`;
    })
    .join("");
  let isi = `<p class="muted">Pilih atau unggah kelas terlebih dahulu.</p>`;
  if (kelas && !tabSiswa) {
    const rows = daftar
      .map((s) => {
        const rec = lihatRaport(state, s.id);
        const sel = (bidang) => `<select data-raport="${esc(s.id)}" data-field="bidang.${bidang}.predikat"><option value="">—</option>${PREDIKAT.map((p) => `<option value="${p.id}" ${rec.bidang[bidang].predikat === p.id ? "selected" : ""}>${p.id}</option>`).join("")}</select>`;
        return `<tr><td>${esc(s.noAbsen || "")}</td><td>${esc(s.nama)}</td><td>${sel("pribadi")}</td><td>${sel("sosial")}</td><td>${sel("belajar")}</td><td>${sel("karir")}</td></tr>`;
      })
      .join("");
    isi = `<p class="kecil">Pilih predikat di tabel, atau unduh blanko Excel per kelas, isi SB / BSH / MB / BB, lalu unggah. Uraian kosong terisi otomatis dan dapat diubah pada tab Per siswa.</p>
      <div class="aksi">
        <button type="button" class="btn btn-gold" data-act="unduh-blanko-predikat">Unduh blanko predikat</button>
        <button type="button" class="btn" data-act="unduh-contoh-predikat">Unduh contoh predikat</button>
        <button type="button" class="btn btn-primary" data-act="pilih-berkas-predikat">Unggah predikat</button>
        <button type="button" class="btn" data-act="susun-kelas">Susun uraian yang masih kosong</button>
      </div>
      <div class="zona" id="zona-predikat" style="margin-top:10px">
        <strong>Letakkan berkas Excel predikat di sini</strong>
        <p class="kecil">Kolom: NISN, Nama, Absen, Pribadi, Sosial, Belajar, Karir. Predikat: SB, BSH, MB, BB.</p>
      </div>
      <input id="berkas-predikat" class="sr" type="file" accept=".csv,.txt,.xlsx,.xls">
      <table class="data" style="margin-top:12px"><thead><tr><th>Absen</th><th>Nama</th><th>Pribadi</th><th>Sosial</th><th>Belajar</th><th>Karir</th></tr></thead><tbody>${rows || `<tr><td colspan="6">Belum ada murid.</td></tr>`}</tbody></table>`;
  } else if (siswa) {
    const rec = lihatRaport(state, siswa.id);
    const bidang = BIDANG.map((b) => {
      const item = rec.bidang[b.id];
      const cek = INDIKATOR[b.id]
        .map((ind) => `<label class="cek"><input type="checkbox" data-raport="${esc(siswa.id)}" data-field="bidang.${b.id}.indikator.${ind.id}" ${item.indikator[ind.id] ? "checked" : ""}> ${esc(ind.label)}</label>`)
        .join("");
      return `<section class="panel" style="margin-bottom:10px">
        <h3>${esc(b.nama)}</h3>
        ${seg(siswa.id, b.id, item.predikat)}
        <details><summary>Indikator yang tampak</summary>${cek}</details>
        <label class="field"><span>Uraian raport</span><textarea data-raport="${esc(siswa.id)}" data-field="bidang.${b.id}.deskripsi">${esc(item.deskripsi)}</textarea></label>
        <button type="button" class="btn btn-kecil" data-act="susun-bidang" data-siswa="${esc(siswa.id)}" data-bidang="${b.id}">Susun uraian dari predikat</button>
      </section>`;
    }).join("");
    const profil = PROFIL.map((p) => `<tr>
      <td>${esc(p.nama)}</td>
      <td><select data-raport="${esc(siswa.id)}" data-field="profil.${p.id}.capaian"><option value="">—</option>${PREDIKAT.map((x) => `<option value="${x.id}" ${rec.profil[p.id].capaian === x.id ? "selected" : ""}>${x.id}</option>`).join("")}</select></td>
      <td><textarea data-raport="${esc(siswa.id)}" data-field="profil.${p.id}.deskripsi">${esc(rec.profil[p.id].deskripsi)}</textarea></td>
    </tr>`).join("");
    const prinsip = PRINSIP.map((p) => `<label class="field"><span>${esc(p.nama)}</span><input data-raport="${esc(siswa.id)}" data-field="prinsipCatatan.${p.id}" value="${esc(rec.prinsipCatatan[p.id])}" placeholder="${esc(p.makna)}"></label>`).join("");
    const pengalaman = PENGALAMAN.map((p) => `<label class="field"><span>${esc(p.nama)}</span><input data-raport="${esc(siswa.id)}" data-field="pengalamanCatatan.${p.id}" value="${esc(rec.pengalamanCatatan[p.id])}"></label>`).join("");
    const olah = OLAH.map((o) => `<label class="field"><span>${esc(o.nama)}</span><input data-raport="${esc(siswa.id)}" data-field="olah.${o.id}" value="${esc(rec.olah[o.id])}" placeholder="${esc(o.petunjuk)}"></label>`).join("");
    const hadir = ["hadir", "sakit", "izin", "alfa"]
      .map((k) => `<label class="field"><span>${k[0].toUpperCase() + k.slice(1)}</span><input inputmode="numeric" data-raport="${esc(siswa.id)}" data-field="kehadiran.${k}" value="${esc(rec.kehadiran[k])}"></label>`)
      .join("");
    isi = `<div class="form-raport">
      <div class="aksi">
        <button type="button" class="btn" data-act="geser" data-arah="-1">Murid sebelumnya</button>
        <button type="button" class="btn" data-act="geser" data-arah="1">Murid berikutnya</button>
        <button type="button" class="btn" data-act="cetak-siswa" data-id="${esc(siswa.id)}">Cetak raport ini</button>
      </div>
      <h2>${esc(siswa.nama)}</h2>
      <p class="kecil">Kelas ${esc(kelas?.nama || "—")} · ${esc(state.periode.tahunAjaran)} semester ${esc(state.periode.semester)}</p>
      <h3>Bidang layanan</h3>
      ${bidang}
      <section class="panel">
        <h3>Dimensi profil lulusan</h3>
        <p class="kecil">Delapan dimensi pendekatan Pembelajaran Mendalam. Tombol di bawah menyalin predikat bidang yang terdekat, lalu tetap dapat diubah.</p>
        <button type="button" class="btn" data-act="isi-profil" data-siswa="${esc(siswa.id)}">Isi capaian awal dari bidang layanan</button>
        <table class="data"><thead><tr><th>Dimensi</th><th>Capaian</th><th>Uraian</th></tr></thead><tbody>${profil}</tbody></table>
        <div class="dua"><div>${prinsip}</div><div>${pengalaman}</div></div>
        <h3>Olah utuh</h3>
        <div class="dua">${olah}</div>
      </section>
      <section class="panel" style="margin-top:10px">
        <h3>Kehadiran layanan</h3>
        <div class="grid-3">${hadir}</div>
        <h3>Catatan guru BK dan tindak lanjut</h3>
        <p class="kecil">Kolom yang masih kosong dapat disusun dari predikat bidang dan topik layanan. Tulisan yang sudah ada tidak diganti.</p>
        <div class="aksi"><button type="button" class="btn" data-act="isi-catatan-guru" data-siswa="${esc(siswa.id)}">Susun catatan guru BK yang masih kosong</button></div>
        <label class="field"><span>Kekuatan</span><textarea data-raport="${esc(siswa.id)}" data-field="kekuatan">${esc(rec.kekuatan)}</textarea></label>
        <label class="field"><span>Perlu pendampingan</span><textarea data-raport="${esc(siswa.id)}" data-field="pendampingan">${esc(rec.pendampingan)}</textarea></label>
        <label class="field"><span>Catatan perkembangan untuk raport</span><textarea data-raport="${esc(siswa.id)}" data-field="catatanGuru">${esc(rec.catatanGuru)}</textarea></label>
        <label class="field"><span>Rekomendasi bagi orang tua</span><textarea data-raport="${esc(siswa.id)}" data-field="rekomendasiOrangtua">${esc(rec.rekomendasiOrangtua)}</textarea></label>
        <label class="field"><span>Tindak lanjut</span><textarea data-raport="${esc(siswa.id)}" data-field="tindakLanjut">${esc(rec.tindakLanjut)}</textarea></label>
        <label class="field"><span>Catatan rahasia guru BK — tidak dicetak</span><textarea data-raport="${esc(siswa.id)}" data-field="catatanRahasia">${esc(rec.catatanRahasia)}</textarea></label>
      </section>
    </div>`;
  }
  return `${kepala("Isi raport", "Capaian bersifat perkembangan: Sangat Berkembang, Berkembang Sesuai Harapan, Mulai Berkembang, atau Belum Berkembang.")}
    ${chips(state, ui)}
    <div class="chips">
      <button type="button" class="chip ${tabSiswa ? "on" : ""}" data-act="tab-raport" data-tab="siswa">Per siswa</button>
      <button type="button" class="chip ${tabSiswa ? "" : "on"}" data-act="tab-raport" data-tab="cepat">Cepat per kelas</button>
    </div>
    <div class="${tabSiswa ? "split" : ""}">
      ${tabSiswa ? `<div class="daftar-siswa">${daftarHtml || `<p class="muted">Kelas belum memiliki murid.</p>`}</div>` : ""}
      <div>${isi}</div>
    </div>`;
}

function formLayanan(state, draft) {
  if (!draft) return "";
  const murid = draft.kelasId ? siswaDiKelas(state, draft.kelasId) : [];
  const cekPrinsip = PRINSIP.map((p) => `<label class="cek"><input type="checkbox" data-draft="prinsip.${p.id}" ${draft.prinsip[p.id] ? "checked" : ""}> ${esc(p.nama)}</label>`).join("");
  const cekPengalaman = PENGALAMAN.map((p) => `<label class="cek"><input type="checkbox" data-draft="pengalaman.${p.id}" ${draft.pengalaman[p.id] ? "checked" : ""}> ${esc(p.nama)}</label>`).join("");
  const cekDim = PROFIL.map((p) => `<label class="cek"><input type="checkbox" data-dim="${p.id}" ${draft.dimensi.includes(p.id) ? "checked" : ""}> ${esc(p.nama)}</label>`).join("");
  const cekMurid = murid
    .map((s) => `<label class="cek"><input type="checkbox" data-pick="${esc(s.id)}" ${draft.siswaIds.includes(s.id) ? "checked" : ""}> ${esc(s.nama)}</label>`)
    .join("");
  return `<div class="panel" style="margin-bottom:14px">
    <h2>${draft.id ? "Ubah layanan" : "Catat layanan"}</h2>
    <div class="dua">
      <label class="field"><span>Tanggal</span><input type="date" data-draft="tanggal" value="${esc(draft.tanggal)}"></label>
      <label class="field"><span>Jenis</span><select data-draft="jenis">${JENIS_LAYANAN.map((j) => `<option ${draft.jenis === j ? "selected" : ""}>${esc(j)}</option>`).join("")}</select></label>
      <label class="field"><span>Bidang</span><select data-draft="bidang">${BIDANG.map((b) => `<option value="${b.id}" ${draft.bidang === b.id ? "selected" : ""}>${esc(b.nama)}</option>`).join("")}</select></label>
      <label class="field"><span>Kelas</span><select data-draft="kelasId"><option value="">Pilih kelas</option>${opsiKelas(state, draft.kelasId)}</select></label>
    </div>
    <div class="cek"><label class="cek"><input type="radio" name="sasaran" data-draft="sasaran" value="kelas" ${draft.sasaran === "kelas" ? "checked" : ""}> Seluruh kelas saat ini</label>
    <label class="cek"><input type="radio" name="sasaran" data-draft="sasaran" value="siswa" ${draft.sasaran === "siswa" ? "checked" : ""}> Murid tertentu</label></div>
    ${draft.sasaran === "siswa" ? `<div class="aksi"><button type="button" class="btn btn-kecil" data-act="pilih-semua">Pilih semua murid kelas</button></div><div class="dua">${cekMurid || `<p class="muted">Kelas belum memiliki murid.</p>`}</div>` : ""}
    <label class="field"><span>Topik</span><input data-draft="topik" value="${esc(draft.topik)}" autocomplete="off"></label>
    <label class="field"><span>Tujuan</span><textarea data-draft="tujuan">${esc(draft.tujuan)}</textarea></label>
    <label class="field"><span>Catatan pelaksanaan</span><textarea data-draft="catatan">${esc(draft.catatan)}</textarea></label>
    <div class="dua"><div><strong>Prinsip pembelajaran mendalam</strong>${cekPrinsip}</div><div><strong>Pengalaman belajar</strong>${cekPengalaman}</div></div>
    <details><summary>Dimensi profil lulusan yang dikuatkan</summary><div class="dua">${cekDim}</div></details>
    <label class="cek"><input type="checkbox" data-draft="rahasia" ${draft.rahasia ? "checked" : ""}> Rahasiakan isi dari raport. Pada cetakan hanya tertulis bahwa layanan individual pernah diberikan.</label>
    <div class="aksi" style="margin-top:8px">
      <button type="button" class="btn btn-primary" data-act="simpan-layanan">Simpan layanan</button>
      <button type="button" class="btn" data-act="batal-layanan">Batal</button>
    </div>
  </div>`;
}

function layanan(state, ui) {
  const daftar = state.layanan.filter((l) => l.tahunAjaran === state.periode.tahunAjaran && l.semester === state.periode.semester);
  const baris = daftar
    .map((l) => {
      const kelas = state.kelas.find((k) => k.id === l.kelasId);
      return `<tr>
        <td>${esc(l.tanggal)}</td>
        <td>${esc(l.jenis)}</td>
        <td>${esc(kelas?.nama || "—")}</td>
        <td>${esc(l.topik)} ${l.rahasia ? `<span class="badge rahasia">Rahasia</span>` : ""}</td>
        <td>${(l.siswaIds || []).length}</td>
        <td class="aksi">
          <button type="button" class="btn btn-kecil" data-act="ubah-layanan" data-id="${esc(l.id)}">Ubah</button>
          <button type="button" class="btn btn-kecil btn-danger" data-act="hapus-layanan" data-id="${esc(l.id)}">Hapus</button>
        </td>
      </tr>`;
    })
    .join("");
  return `${kepala("Layanan BK", "Catatan layanan mengisi bagian partisipasi raport. Layanan klasikal menempel pada murid yang ada di kelas pada saat disimpan.", `<button type="button" class="btn btn-primary" data-act="baru-layanan">${ui.draftLayanan ? "Tutup form" : "Catat layanan"}</button>`)}
    ${formLayanan(state, ui.draftLayanan)}
    <table class="data">
      <thead><tr><th>Tanggal</th><th>Jenis</th><th>Kelas</th><th>Topik</th><th>Murid</th><th></th></tr></thead>
      <tbody>${baris || `<tr><td colspan="6">Belum ada layanan pada semester ini.</td></tr>`}</tbody>
    </table>`;
}

function cetak(state, ui) {
  const daftar = ui.kelasId ? siswaDiKelas(state, ui.kelasId) : [];
  const kontrolSiswa = `<label class="field"><span>Kelas</span><select data-ui="kelasId">${opsiKelas(state, ui.kelasId)}</select></label>
    <label class="field"><span>Murid</span><select data-ui="siswaId">${daftar.map((s) => `<option value="${esc(s.id)}" ${s.id === ui.siswaId ? "selected" : ""}>${esc(s.nama)}</option>`).join("")}</select></label>`;
  const kontrolKelas = `<label class="field"><span>Kelas</span><select data-ui="kelasId">${opsiKelas(state, ui.kelasId)}</select></label>
    <label class="cek"><input type="checkbox" data-ui-cek="lengkap" ${ui.lengkap ? "checked" : ""}> Ikutkan raport lengkap setiap murid. Tanpa centang ini, yang tercetak adalah rekap kelas.</label>`;
  const namaKelas = state.kelas.find((k) => k.id === ui.kelasId)?.nama || "";
  return `<div class="screen-only">${kepala("Cetak raport", "Pilih cetak satu murid atau satu kelas. Di jendela cetak, pilih printer atau Simpan sebagai PDF.")}
    <div class="pilih-cetak">
      <button type="button" class="${ui.cetakMode === "siswa" ? "on" : ""}" data-act="mode-cetak" data-mode="siswa"><strong>Cetak per siswa</strong><span class="kecil">Satu laporan lengkap untuk orang tua dan arsip.</span></button>
      <button type="button" class="${ui.cetakMode === "kelas" ? "on" : ""}" data-act="mode-cetak" data-mode="kelas"><strong>Cetak per kelas</strong><span class="kecil">Rekap wali kelas, atau rekap ditambah raport setiap murid.</span></button>
    </div>
    <div class="panel">
      <div class="dua">
        ${ui.cetakMode === "siswa" ? kontrolSiswa : kontrolKelas}
        <label class="field"><span>Tanggal laporan</span><input type="date" id="tanggal-cetak" value="${esc(ui.tanggalCetak)}"></label>
      </div>
      <button type="button" class="btn btn-primary" data-act="cetak-sekarang">Cetak / simpan PDF</button>
    </div>
    <div class="panel" style="margin-top:12px">
      <h2>Blanko Excel poin D, E, dan F${namaKelas ? ` · kelas ${esc(namaKelas)}` : ""}</h2>
      <p class="kecil">Unduh blanko atau contoh pengisian per kelas, isi di Excel, lalu unggah kembali. Lembar <strong>D dan F</strong> mengisi Pembelajaran Mendalam serta catatan guru BK. Lembar <strong>E Layanan</strong> menambah partisipasi layanan. Kolom kosong tidak menimpa data yang sudah ada. NISN sasaran kosong pada lembar E berarti seluruh kelas.</p>
      <div class="aksi">
        <button type="button" class="btn btn-gold" data-act="unduh-blanko-def">Unduh blanko</button>
        <button type="button" class="btn" data-act="unduh-contoh-def">Unduh contoh pengisian</button>
        <button type="button" class="btn btn-primary" data-act="pilih-berkas-def">Unggah form terisi</button>
      </div>
      <div class="zona" id="zona-def" style="margin-top:10px">
        <strong>Atau letakkan berkas Excel di sini</strong>
        <p class="kecil">Format .xlsx atau .xls sesuai blanko kelas yang dipilih di atas.</p>
      </div>
      <input id="berkas-def" class="sr" type="file" accept=".csv,.txt,.xlsx,.xls">
    </div>
    </div>
    <div class="sheets">${htmlCetak(state, { mode: ui.cetakMode, kelasId: ui.kelasId, siswaId: ui.siswaId, lengkap: ui.lengkap, tanggal: ui.tanggalCetak })}</div>`;
}

function rencanaHtml(ui) {
  if (!ui.kenaikan) return "";
  const items = ui.kenaikan.items;
  const naik = items.filter((i) => i.status === "naik").length;
  const lulus = items.filter((i) => i.status === "lulus").length;
  const tetap = items.filter((i) => i.status === "tetap").length;
  const baris = items
    .slice(0, 15)
    .map((i) => `<tr><td>${esc(i.nama)}</td><td>${esc(i.dari)}</td><td>${i.status === "lulus" ? "Lulus, tidak masuk tahun baru" : esc(i.ke || "—")}</td></tr>`)
    .join("");
  return `<div class="panel" style="margin-top:10px">
    <p>${naik} naik kelas, ${tetap} tetap di nama kelas yang sama, ${lulus} tingkat 9 tidak disalin.</p>
    <label class="field"><span>Tahun ajaran tujuan</span><input id="tahun-baru" value="${esc(ui.kenaikan.tahunBaru)}" autocomplete="off"></label>
    <table class="data"><thead><tr><th>Nama</th><th>Dari</th><th>Menjadi</th></tr></thead><tbody>${baris}</tbody></table>
    ${items.length > 15 ? `<p class="kecil">Menampilkan 15 dari ${items.length} murid.</p>` : ""}
    <div class="aksi">
      <button type="button" class="btn btn-primary" data-act="kenaikan-ya">Terapkan kenaikan</button>
      <button type="button" class="btn" data-act="kenaikan-batal">Batal</button>
    </div>
  </div>`;
}

function pengaturan(state, ui) {
  const s = state.sekolah;
  const g = state.guru;
  const origin = location.origin;
  return `${kepala("Pengaturan", "Identitas ini tercetak pada kop dan tanda tangan raport.")}
    <div class="grid-2">
      <div class="card">
        <h2>Guru BK</h2>
        <label class="field"><span>Nama</span><input data-bind="guru.nama" value="${esc(g.nama)}" autocomplete="name"></label>
        <label class="field"><span>NBM</span><input data-bind="guru.nip" value="${esc(g.nip)}" autocomplete="off" placeholder="NBM guru BK"></label>
        <label class="field"><span>Email</span><input data-bind="guru.email" value="${esc(g.email)}" autocomplete="email"></label>
        <label class="field"><span>Jabatan pada raport</span><input data-bind="guru.jabatan" value="${esc(g.jabatan)}"></label>
        <h2>Kepala sekolah</h2>
        <label class="field"><span>Nama</span><input data-bind="sekolah.kepalaSekolah" value="${esc(s.kepalaSekolah)}"></label>
        <label class="field"><span>NBM</span><input data-bind="sekolah.nipKepalaSekolah" value="${esc(s.nipKepalaSekolah)}" placeholder="NBM kepala sekolah"></label>
        <label class="field"><span>Kota pada tanggal laporan</span><input data-bind="sekolah.kota" value="${esc(s.kota)}"></label>
      </div>
      <div class="card">
        <h2>Kop sekolah</h2>
        <label class="field"><span>Nama sekolah</span><input data-bind="sekolah.nama" value="${esc(s.nama)}"></label>
        <label class="field"><span>Yayasan / persyarikatan</span><input data-bind="sekolah.yayasan" value="${esc(s.yayasan)}"></label>
        <label class="field"><span>NPSN</span><input data-bind="sekolah.npsn" value="${esc(s.npsn)}"></label>
        <label class="field"><span>Alamat</span><textarea data-bind="sekolah.alamat">${esc(s.alamat)}</textarea></label>
        <div class="dua">
          <label class="field"><span>Telepon</span><input data-bind="sekolah.telepon" value="${esc(s.telepon)}"></label>
          <label class="field"><span>Email sekolah</span><input data-bind="sekolah.email" value="${esc(s.email)}"></label>
        </div>
      </div>
    </div>
    <div class="card" style="margin-top:14px">
      <h2>Google Drive akun guru</h2>
      <p>Cara yang paling mudah: masuk ke aplikasi Google Drive di komputer dengan akun guru, lalu pilih folder Drive tersebut. Aplikasi membuat folder <strong>Raport BK SMP Muhammadiyah 22 Setiabudi Pamulang</strong> di dalamnya.</p>
      <div class="aksi">
        <button type="button" class="btn btn-primary" data-act="sambung-folder">Pilih folder Google Drive</button>
        ${status.folder === "needs-permission" ? `<button type="button" class="btn" data-act="izin-folder">Izinkan folder lagi</button>` : ""}
        <button type="button" class="btn" data-act="unduh-json">Unduh cadangan JSON</button>
        <button type="button" class="btn" data-act="pilih-json">Muat cadangan JSON</button>
        <input id="berkas-json" class="sr" type="file" accept="application/json,.json">
      </div>
      <h3>Masuk langsung ke akun Google</h3>
      <p class="kecil">Lakukan sekali bila ingin menulis ke Drive tanpa aplikasi desktop. Di Google Cloud Console, buat OAuth Client ID jenis Web application. Tambahkan origin <strong>${esc(origin)}</strong>. Aktifkan Google Drive API. Tempel Client ID di bawah.</p>
      <label class="field"><span>Client ID</span><input id="client-id" value="${esc(clientTersimpan())}" autocomplete="off" placeholder="xxxx.apps.googleusercontent.com"></label>
      <div class="aksi">
        <button type="button" class="btn" data-act="simpan-client">Simpan Client ID</button>
        <button type="button" class="btn btn-primary" data-act="masuk-google">Masuk dengan Google</button>
        <button type="button" class="btn" data-act="unggah-google">Unggah ke Drive</button>
        <button type="button" class="btn" data-act="muat-google">Muat dari Drive</button>
      </div>
      ${status.googleError ? `<p class="kecil">${esc(status.googleError)}</p>` : ""}
    </div>
    <div class="card" style="margin-top:14px">
      <h2>Tahun ajaran berikutnya</h2>
      <p class="kecil">Kelas 7 menjadi 8, kelas 8 menjadi 9. Kelas 9 tidak disalin karena dianggap lulus. Raport semester lama tetap tersimpan.</p>
      <button type="button" class="btn" data-act="kenaikan-lihat">Lihat rencana kenaikan</button>
      ${rencanaHtml(ui)}
    </div>
    <div class="card" style="margin-top:14px">
      <h2>Hapus data murid</h2>
      <p class="kecil">Menghapus kelas, murid, layanan, dan raport di komputer ini. Identitas sekolah dan guru tetap. Folder Drive tidak dihapus sampai Anda menyimpan lagi.</p>
      <button type="button" class="btn btn-danger" data-act="hapus-data">Hapus daftar dan raport</button>
    </div>`;
}

function panduan() {
  return `${kepala("Panduan", "Aplikasi ini berjalan di komputer guru. Internet hanya diperlukan saat masuk Google atau saat Google Drive menyinkronkan folder.")}
    <div class="card">
      <h2>Membuka aplikasi</h2>
      <ol>
        <li>Klik dua kali <strong>Raport BK SMPM 22.exe</strong>.</li>
        <li>Biarkan jendela hitam tetap terbuka selama raport dipakai.</li>
        <li>Gunakan Google Chrome atau Microsoft Edge agar folder Drive dapat dipilih.</li>
      </ol>
      <h2>Menyimpan ke Google Drive guru</h2>
      <ol>
        <li>Masuk ke aplikasi Google Drive untuk desktop dengan akun guru.</li>
        <li>Di aplikasi ini pilih <strong>Sambungkan folder Google Drive</strong>, lalu tunjuk folder Drive akun tersebut.</li>
        <li>Setiap perubahan tersimpan di komputer dan di folder itu. Saat internet ada, aplikasi Drive mengunggahnya ke akun guru.</li>
      </ol>
      <p>Masuk dengan akun Google di menu Pengaturan menulis berkas yang sama langsung ke Drive awan. Cara itu meminta Client ID sekali. Saat offline, isian tetap aman di komputer dan terunggah setelah masuk kembali.</p>
      <h2>Daftar murid</h2>
      <p>Unduh template Excel, isi nama sesuai kelas, lalu unggah. Daftar murid yang sudah ada akan terhapus dan diganti seluruhnya dengan isi berkas tersebut.</p>
      <h2>Isi yang tercetak</h2>
      <p>Raport memuat empat bidang layanan BK (pribadi, sosial, belajar, karir), delapan dimensi profil lulusan Pembelajaran Mendalam, serta prinsip berkesadaran, bermakna, dan menggembirakan. Pengalaman belajarnya: memahami, mengaplikasi, dan merefleksi.</p>
      <h2>Cetak</h2>
      <p>Menu Cetak menyediakan raport satu murid dan rekap satu kelas. Centang ikutkan raport lengkap bila satu kelas ingin dicetak sekaligus berikut uraian setiap murid. Pilih Simpan sebagai PDF bila ingin arsip digital.</p>
      <h2>Kerahasiaan</h2>
      <p>Catatan bertanda rahasia dan catatan rahasia pada formulir murid tidak masuk lembar yang dicetak untuk orang tua. Berkas JSON tetap berisi catatan itu. Simpan hanya di Drive guru BK dan jangan dibagikan ke murid atau grup orang tua.</p>
    </div>`;
}

function modal(ui) {
  if (!ui.modal) return "";
  if (ui.modal.jenis === "konflik") {
    const remote = ui.modal.remote;
    const lokalJam = fmt(ui.modal.lokalUpdated);
    const remoteJam = fmt(remote?.meta?.updatedAt);
    return `<div class="modal screen-only">
      <div class="dialog">
        <h2>Ada dua data raport</h2>
        <p>Data di ${esc(ui.modal.sumber)} terakhir berubah ${esc(remoteJam)}. Data yang sedang terbuka terakhir berubah ${esc(lokalJam)}. Memilih salah satu akan menggantikan yang lain pada simpanan berikutnya.</p>
        <p class="kecil">${remote?.siswa?.length || 0} murid pada data ${esc(ui.modal.sumber)}.</p>
        <div class="aksi">
          <button type="button" class="btn btn-primary" data-act="pakai-remote">Pakai data ${esc(ui.modal.sumber)}</button>
          <button type="button" class="btn" data-act="pakai-lokal">Tetap pakai data yang sedang terbuka</button>
        </div>
      </div>
    </div>`;
  }
  if (ui.modal.jenis === "hapus") {
    return `<div class="modal screen-only">
      <div class="dialog">
        <h2>Hapus data murid dan raport?</h2>
        <p>Ketik HAPUS untuk melanjutkan. Tindakan ini membersihkan data di komputer ini.</p>
        <label class="field"><span>Konfirmasi</span><input id="wipe-text" autocomplete="off"></label>
        <div class="aksi">
          <button type="button" class="btn btn-danger" data-act="hapus-ya">Hapus</button>
          <button type="button" class="btn" data-act="tutup-modal">Batal</button>
        </div>
      </div>
    </div>`;
  }
  return "";
}

function fmt(iso) {
  if (!iso) return "pada waktu yang tidak tercatat";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "pada waktu yang tidak tercatat";
  return d.toLocaleString("id-ID");
}

export function tampilan(state, ui, route) {
  const halaman = {
    beranda: beranda(state),
    murid: murid(state, ui),
    raport: raport(state, ui),
    layanan: layanan(state, ui),
    cetak: cetak(state, ui),
    pengaturan: pengaturan(state, ui),
    panduan: panduan(),
  }[route] || beranda(state);
  const bungkus = route === "cetak" ? halaman : `<div class="page screen-only">${halaman}</div>`;
  return `<div class="app">${aside(state, route)}<section class="main">${bungkus}</section><footer class="statusbar screen-only"><span id="status-line"></span></footer></div>${modal(ui)}`;
}
