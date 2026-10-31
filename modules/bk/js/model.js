export const FOLDER_NAME = "Raport BK SMP Muhammadiyah 22 Setiabudi Pamulang";
export const FILE_NAME = "raport-bk-smpm22.json";

export const SEKOLAH_DEFAULT = {
  nama: "SMP MUHAMMADIYAH 22 SETIABUDI PAMULANG",
  npsn: "20603577",
  alamat: "Jalan Surya Kencana No. 29, Pamulang Barat, Kec. Pamulang, Kota Tangerang Selatan, Banten 15417",
  telepon: "(021) 74706439",
  email: "smpmuh22pamulang@gmail.com",
  website: "www.smpm22pamulang.sch.id",
  yayasan: "Persyarikatan Muhammadiyah",
  kota: "Pamulang",
  kepalaSekolah: "",
  nipKepalaSekolah: "",
  fase: "D",
};

export const BIDANG = [
  { id: "pribadi", nama: "Pribadi" },
  { id: "sosial", nama: "Sosial" },
  { id: "belajar", nama: "Belajar" },
  { id: "karir", nama: "Karir" },
];

export const INDIKATOR = {
  pribadi: [
    { id: "potensi", label: "mengenal potensi, minat, dan kelebihan diri" },
    { id: "emosi", label: "mengelola emosi dan tekanan secara sehat" },
    { id: "akhlak", label: "menunjukkan akhlak dan tanggung jawab pribadi" },
    { id: "menerima", label: "menerima kondisi diri secara positif" },
  ],
  sosial: [
    { id: "santun", label: "berinteraksi secara santun dengan teman, guru, dan orang tua" },
    { id: "kerjasama", label: "bekerja sama dan bergotong royong" },
    { id: "beda", label: "menghargai perbedaan" },
    { id: "konflik", label: "menyelesaikan perbedaan pendapat secara damai" },
  ],
  belajar: [
    { id: "teratur", label: "memiliki kebiasaan belajar yang teratur" },
    { id: "waktu", label: "mengatur waktu dan strategi belajar" },
    { id: "mandiri", label: "menunjukkan kemandirian belajar" },
    { id: "asesmen", label: "menyiapkan diri menghadapi tugas dan asesmen" },
  ],
  karir: [
    { id: "minat", label: "mengenal minat dan cita-cita" },
    { id: "kaitan", label: "memahami kaitan belajar dengan masa depan" },
    { id: "lanjut", label: "menggali informasi pendidikan lanjutan" },
    { id: "rencana", label: "merencanakan langkah pengembangan diri" },
  ],
};

export const PREDIKAT = [
  { id: "SB", nama: "Sangat Berkembang" },
  { id: "BSH", nama: "Berkembang Sesuai Harapan" },
  { id: "MB", nama: "Mulai Berkembang" },
  { id: "BB", nama: "Belum Berkembang" },
];

export const PROFIL = [
  { id: "keimanan", nama: "Keimanan dan ketakwaan kepada Tuhan Yang Maha Esa", dari: "pribadi" },
  { id: "kewargaan", nama: "Kewargaan", dari: "sosial" },
  { id: "nalar", nama: "Penalaran kritis", dari: "belajar" },
  { id: "kreativitas", nama: "Kreativitas", dari: "belajar" },
  { id: "kolaborasi", nama: "Kolaborasi", dari: "sosial" },
  { id: "kemandirian", nama: "Kemandirian", dari: "belajar" },
  { id: "kesehatan", nama: "Kesehatan", dari: "pribadi" },
  { id: "komunikasi", nama: "Komunikasi", dari: "sosial" },
];

export const PRINSIP = [
  { id: "berkesadaran", nama: "Berkesadaran", makna: "Murid sadar tujuan, aktif, dan mampu mengatur dirinya." },
  { id: "bermakna", nama: "Bermakna", makna: "Layanan terhubung dengan kehidupan dan pengalaman nyata." },
  { id: "menggembirakan", nama: "Menggembirakan", makna: "Suasana positif, menantang, dan menghargai keterlibatan." },
];

export const PENGALAMAN = [
  { id: "memahami", nama: "Memahami" },
  { id: "mengaplikasi", nama: "Mengaplikasi" },
  { id: "merefleksi", nama: "Merefleksi" },
];

export const OLAH = [
  { id: "pikir", nama: "Olah pikir", petunjuk: "Cara menalar, bertanya, dan memecahkan masalah" },
  { id: "hati", nama: "Olah hati", petunjuk: "Akhlak, empati, dan tanggung jawab" },
  { id: "rasa", nama: "Olah rasa", petunjuk: "Kepekaan sosial dan penghargaan terhadap sesama" },
  { id: "raga", nama: "Olah raga", petunjuk: "Kesehatan, kebugaran, dan perawatan diri" },
];

export const JENIS_LAYANAN = [
  "Bimbingan klasikal",
  "Bimbingan kelompok",
  "Konseling kelompok",
  "Konseling individual",
  "Konsultasi",
  "Kolaborasi",
  "Mediasi",
  "Kunjungan rumah",
  "Layanan peminatan",
  "Advokasi",
];

const BUKAAN = {
  pribadi: {
    SB: (n) => `${n} sangat baik dalam mengenali potensi diri, mengelola emosi, dan bertanggung jawab atas pilihannya.`,
    BSH: (n) => `${n} mampu mengenali dirinya dan menunjukkan tanggung jawab pribadi sesuai harapan usianya.`,
    MB: (n) => `${n} mulai mengenali dirinya, tetapi pengelolaan emosi dan tanggung jawab masih perlu dilatih.`,
    BB: (n) => `${n} belum stabil dalam mengenali diri dan mengelola emosi, sehingga perlu pendampingan dekat.`,
  },
  sosial: {
    SB: (n) => `${n} sangat baik dalam bekerja sama, menghargai perbedaan, dan menjaga hubungan yang santun.`,
    BSH: (n) => `${n} mampu bergaul secara santun dan bekerja sama sesuai harapan.`,
    MB: (n) => `${n} mulai mampu bergaul dan bekerja sama, tetapi masih perlu bimbingan saat menghadapi perbedaan atau konflik.`,
    BB: (n) => `${n} masih kesulitan menjalin kerja sama dan interaksi yang positif, sehingga perlu pendampingan sosial yang terarah.`,
  },
  belajar: {
    SB: (n) => `${n} sangat baik dalam mengatur belajar, menjaga kemandirian, dan menyiapkan diri menghadapi tugas.`,
    BSH: (n) => `${n} menunjukkan kebiasaan belajar yang sesuai harapan dan cukup mandiri.`,
    MB: (n) => `${n} mulai membangun kebiasaan belajar, tetapi kemandirian dan keteraturan masih perlu penguatan.`,
    BB: (n) => `${n} belum menunjukkan kebiasaan belajar yang teratur dan masih bergantung pada arahan orang lain.`,
  },
  karir: {
    SB: (n) => `${n} sangat baik dalam mengenali minat, mengaitkan belajar dengan cita-cita, dan merencanakan pendidikan lanjutan.`,
    BSH: (n) => `${n} memiliki gambaran minat dan cita-cita yang sesuai harapan usianya.`,
    MB: (n) => `${n} mulai mengenali minat dan cita-cita, tetapi rencana pendidikannya masih perlu diperjelas.`,
    BB: (n) => `${n} belum memiliki gambaran minat dan rencana pendidikan lanjutan, sehingga perlu layanan peminatan yang lebih intensif.`,
  },
};

const PENUTUP = {
  SB: "Kebiasaan ini layak dipertahankan.",
  BSH: "Penguatan sebaiknya dilanjutkan di rumah dan di sekolah.",
  MB: "Dukungan wali kelas dan orang tua akan membantu perkembangan berikutnya.",
  BB: "Perlu kerja sama sekolah dan orang tua dengan langkah yang konkret dan bertahap.",
};

const HEADER_ALIAS = {
  nisn: ["nisn"],
  nis: ["nis", "nipd", "no induk", "nomor induk"],
  nama: ["nama", "nama siswa", "nama lengkap", "peserta didik", "nama peserta didik"],
  jk: ["jk", "jenis kelamin", "kelamin", "gender"],
  kelas: ["kelas", "rombel", "rombongan belajar", "kelas/rombel"],
  noAbsen: ["no absen", "nomor absen", "absen"],
  tempatLahir: ["tempat lahir", "tpl", "kota lahir"],
  tanggalLahir: ["tanggal lahir", "tgl lahir", "tanggal_lahir"],
  agama: ["agama"],
  namaAyah: ["nama ayah", "ayah", "nama bapak", "nama orang tua"],
  namaIbu: ["nama ibu", "ibu"],
};

export function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[c]));
}

export function uid() {
  if (globalThis.crypto?.randomUUID) return crypto.randomUUID();
  return `id-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

export function deepSet(obj, path, value) {
  const parts = String(path).split(".");
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const p = parts[i];
    if (!cur[p] || typeof cur[p] !== "object") cur[p] = {};
    cur = cur[p];
  }
  cur[parts[parts.length - 1]] = value;
}

export function namaPredikat(id) {
  return PREDIKAT.find((p) => p.id === id)?.nama || "";
}

export function formatTanggalID(iso) {
  const bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"];
  const sumber = iso || new Date().toISOString().slice(0, 10);
  const [y, m, d] = String(sumber).slice(0, 10).split("-");
  if (!y || !m || !d) return "";
  return `${Number(d)} ${bulan[Number(m) - 1] || ""} ${y}`.trim();
}

export function tahunBerikutnya(ta) {
  const m = String(ta).match(/^(\d{4})\s*\/\s*(\d{4})$/);
  if (!m) return "";
  return `${Number(m[1]) + 1}/${Number(m[2]) + 1}`;
}

export function joinDan(arr) {
  const a = arr.filter(Boolean);
  if (a.length <= 1) return a[0] || "";
  if (a.length === 2) return `${a[0]} dan ${a[1]}`;
  return `${a.slice(0, -1).join(", ")}, dan ${a[a.length - 1]}`;
}

export function normKelas(v) {
  const s = String(v || "").trim().replace(/\s+/g, " ").toUpperCase();
  const m = s.match(/^(\d+)\s*([A-Z])$/);
  if (m) return m[1] + m[2];
  return s;
}

export function tingkatDari(nama) {
  const m = String(nama || "").match(/(\d+)/);
  return m ? Number(m[1]) : 0;
}

export function normJk(v) {
  const s = String(v || "").trim().toLowerCase();
  if (["l", "laki-laki", "laki laki", "laki", "pria"].includes(s)) return "L";
  if (["p", "perempuan", "wanita"].includes(s)) return "P";
  return "";
}

export function rapikanNama(n) {
  const kecil = new Set(["bin", "binti", "bint", "al", "van", "der", "de"]);
  return String(n || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ")
    .split(" ")
    .map((w, i) => {
      if (!w) return "";
      if (i > 0 && kecil.has(w)) return w;
      return w.charAt(0).toUpperCase() + w.slice(1);
    })
    .join(" ");
}

export function raportKosong() {
  const bidang = {};
  for (const b of BIDANG) bidang[b.id] = { predikat: "", indikator: {}, deskripsi: "" };
  const profil = {};
  for (const p of PROFIL) profil[p.id] = { capaian: "", deskripsi: "" };
  const olah = {};
  for (const o of OLAH) olah[o.id] = "";
  return {
    bidang,
    profil,
    prinsipCatatan: { berkesadaran: "", bermakna: "", menggembirakan: "" },
    pengalamanCatatan: { memahami: "", mengaplikasi: "", merefleksi: "" },
    olah,
    kehadiran: { hadir: "", sakit: "", izin: "", alfa: "" },
    kekuatan: "",
    pendampingan: "",
    catatanGuru: "",
    rekomendasiOrangtua: "",
    tindakLanjut: "",
    catatanRahasia: "",
    snapshot: null,
  };
}

export function mergeRaport(saved) {
  const base = raportKosong();
  if (!saved) return base;
  for (const b of BIDANG) {
    const s = saved.bidang?.[b.id] || {};
    base.bidang[b.id] = {
      predikat: s.predikat || "",
      deskripsi: s.deskripsi || "",
      indikator: { ...(s.indikator || {}) },
    };
  }
  for (const p of PROFIL) {
    const s = saved.profil?.[p.id] || {};
    base.profil[p.id] = { capaian: s.capaian || "", deskripsi: s.deskripsi || "" };
  }
  base.prinsipCatatan = { ...base.prinsipCatatan, ...(saved.prinsipCatatan || {}) };
  base.pengalamanCatatan = { ...base.pengalamanCatatan, ...(saved.pengalamanCatatan || {}) };
  base.olah = { ...base.olah, ...(saved.olah || {}) };
  base.kehadiran = { ...base.kehadiran, ...(saved.kehadiran || {}) };
  for (const k of ["kekuatan", "pendampingan", "catatanGuru", "rekomendasiOrangtua", "tindakLanjut", "catatanRahasia"]) {
    base[k] = saved[k] || "";
  }
  base.snapshot = saved.snapshot || null;
  return base;
}

export function raportKey(siswaId, tahun, semester) {
  return `${siswaId}|${tahun}|${semester}`;
}

export function lihatRaport(state, siswaId) {
  const key = raportKey(siswaId, state.periode.tahunAjaran, state.periode.semester);
  return mergeRaport(state.raport[key]);
}

export function ensureRaport(state, siswaId) {
  const key = raportKey(siswaId, state.periode.tahunAjaran, state.periode.semester);
  state.raport[key] = mergeRaport(state.raport[key]);
  const s = state.siswa.find((x) => x.id === siswaId);
  const kid = s ? kelasIdPada(state, s) : "";
  const k = state.kelas.find((x) => x.id === kid);
  state.raport[key].snapshot = {
    nama: s?.nama || "",
    nisn: s?.nisn || "",
    nis: s?.nis || "",
    kelas: k?.nama || "",
  };
  return state.raport[key];
}

export function raportTerisiPredikat(rec) {
  return BIDANG.every((b) => rec.bidang[b.id].predikat);
}

export function initialState() {
  return {
    version: 1,
    aplikasi: "Raport BK SMP Muhammadiyah 22 Setiabudi Pamulang",
    sekolah: { ...SEKOLAH_DEFAULT },
    guru: {
      nama: "",
      nip: "",
      email: "",
      jabatan: "Guru Bimbingan dan Konseling",
    },
    periode: { tahunAjaran: "2026/2027", semester: "Ganjil" },
    kelas: [],
    siswa: [],
    penempatan: {},
    layanan: [],
    raport: {},
    meta: {
      updatedAt: null,
      cloudFileId: null,
      cloudFolderId: null,
      googleEmail: "",
      googleName: "",
    },
  };
}

export function migrate(raw) {
  const base = initialState();
  if (!raw || typeof raw !== "object") return base;
  return {
    ...base,
    ...raw,
    sekolah: { ...base.sekolah, ...(raw.sekolah || {}) },
    guru: { ...base.guru, ...(raw.guru || {}) },
    periode: { ...base.periode, ...(raw.periode || {}) },
    kelas: Array.isArray(raw.kelas) ? raw.kelas : [],
    siswa: Array.isArray(raw.siswa) ? raw.siswa : [],
    penempatan: raw.penempatan && typeof raw.penempatan === "object" ? raw.penempatan : {},
    layanan: Array.isArray(raw.layanan) ? raw.layanan : [],
    raport: raw.raport && typeof raw.raport === "object" ? raw.raport : {},
    meta: { ...base.meta, ...(raw.meta || {}) },
    version: 1,
  };
}

export function tahunPunyaPenempatan(state, tahun = state.periode.tahunAjaran) {
  const p = state.penempatan?.[tahun];
  return !!(p && Object.keys(p).length);
}

export function kelasIdPada(state, siswa, tahun = state.periode.tahunAjaran) {
  if (!siswa) return "";
  if (tahunPunyaPenempatan(state, tahun)) return state.penempatan[tahun][siswa.id] || "";
  return siswa.kelasId || "";
}

export function seedPenempatan(state, tahun = state.periode.tahunAjaran) {
  state.penempatan ||= {};
  if (tahunPunyaPenempatan(state, tahun)) return state.penempatan[tahun];
  const map = {};
  for (const s of state.siswa) if (s.kelasId) map[s.id] = s.kelasId;
  state.penempatan[tahun] = map;
  return map;
}

export function tempatkan(state, siswaId, kelasId) {
  const tahun = state.periode.tahunAjaran;
  seedPenempatan(state, tahun);
  state.penempatan[tahun][siswaId] = kelasId || "";
  const s = state.siswa.find((x) => x.id === siswaId);
  if (s) s.kelasId = kelasId || "";
}

export function bandingKelas(a, b) {
  const ta = a.tingkat || tingkatDari(a.nama) || 99;
  const tb = b.tingkat || tingkatDari(b.nama) || 99;
  if (ta !== tb) return ta - tb;
  return String(a.nama).localeCompare(String(b.nama), "id");
}

export function bandingSiswa(a, b) {
  const na = parseInt(a.noAbsen, 10);
  const nb = parseInt(b.noAbsen, 10);
  const aOk = !Number.isNaN(na);
  const bOk = !Number.isNaN(nb);
  if (aOk && bOk && na !== nb) return na - nb;
  if (aOk && !bOk) return -1;
  if (!aOk && bOk) return 1;
  return String(a.nama).localeCompare(String(b.nama), "id");
}

export function siswaDiKelas(state, kelasId, tahun = state.periode.tahunAjaran) {
  return state.siswa.filter((s) => kelasIdPada(state, s, tahun) === kelasId).sort(bandingSiswa);
}

export function kelasTerpakai(state) {
  const tahun = state.periode.tahunAjaran;
  const ids = new Set(state.siswa.map((s) => kelasIdPada(state, s, tahun)).filter(Boolean));
  return state.kelas.filter((k) => ids.has(k.id)).sort(bandingKelas);
}

export function indikatorTerpilih(rec, bidangId) {
  const map = rec.bidang?.[bidangId]?.indikator || {};
  return (INDIKATOR[bidangId] || []).filter((i) => map[i.id]).map((i) => i.label);
}

export function buatDeskripsi(nama, bidangId, predikat, labels) {
  const buka = BUKAAN[bidangId]?.[predikat];
  if (!buka) return "";
  const siapa = nama || "Murid";
  const tengah = labels?.length ? ` Pada semester ini tampak kemampuan murid dalam ${joinDan(labels)}.` : "";
  return `${buka(siapa)}${tengah} ${PENUTUP[predikat]}`.replace(/\s+/g, " ").trim();
}

export function buatDeskripsiProfil(nama, profilId, capaian) {
  const label = PROFIL.find((p) => p.id === profilId)?.nama || "dimensi ini";
  const siapa = nama || "Murid";
  const kalimat = {
    SB: `${siapa} menunjukkan perkembangan yang sangat baik pada dimensi ${label}.`,
    BSH: `${siapa} menunjukkan dimensi ${label} sesuai harapan pada semester ini.`,
    MB: `${siapa} mulai menampakkan dimensi ${label} dan masih perlu penguatan.`,
    BB: `${siapa} masih perlu pendampingan agar dimensi ${label} tumbuh lebih baik.`,
  };
  return kalimat[capaian] || "";
}

export function isiDeskripsiKosong(state, siswaId) {
  const rec = ensureRaport(state, siswaId);
  const siswa = state.siswa.find((s) => s.id === siswaId);
  let n = 0;
  for (const b of BIDANG) {
    const item = rec.bidang[b.id];
    if (item.predikat && !String(item.deskripsi).trim()) {
      item.deskripsi = buatDeskripsi(siswa?.nama, b.id, item.predikat, indikatorTerpilih(rec, b.id));
      n++;
    }
  }
  return n;
}

export function susunUlangBidang(state, siswaId, bidangId) {
  const rec = ensureRaport(state, siswaId);
  const siswa = state.siswa.find((s) => s.id === siswaId);
  const item = rec.bidang[bidangId];
  if (!item.predikat) return false;
  item.deskripsi = buatDeskripsi(siswa?.nama, bidangId, item.predikat, indikatorTerpilih(rec, bidangId));
  return true;
}

export function isiProfilDariBidang(state, siswaId) {
  const rec = ensureRaport(state, siswaId);
  const siswa = state.siswa.find((s) => s.id === siswaId);
  for (const p of PROFIL) {
    const pred = rec.bidang[p.dari]?.predikat || "";
    if (!pred) continue;
    rec.profil[p.id].capaian = pred;
    if (!String(rec.profil[p.id].deskripsi).trim()) {
      rec.profil[p.id].deskripsi = buatDeskripsiProfil(siswa?.nama, p.id, pred);
    }
  }
}

function namaBidangTanpaPredikat(label) {
  return String(label || "").replace(/\s*\([^)]*\)\s*$/, "").trim();
}

export function usulanCatatanGuru(state, siswaId) {
  const siswa = state.siswa.find((s) => s.id === siswaId);
  const rec = lihatRaport(state, siswaId);
  const nama = siswa?.nama || "Murid";
  const layanan = layananUntukSiswa(state, siswaId).filter((l) => !l.rahasia);
  const topik = [];
  for (const l of layanan) {
    if (l.topik && !topik.includes(l.topik)) topik.push(l.topik);
  }
  const kuat = [];
  const lemah = [];
  for (const b of BIDANG) {
    const pred = rec.bidang[b.id]?.predikat;
    if (pred === "SB" || pred === "BSH") kuat.push(`${b.nama.toLowerCase()} (${namaPredikat(pred)})`);
    if (pred === "MB" || pred === "BB") lemah.push(`${b.nama.toLowerCase()} (${namaPredikat(pred)})`);
  }
  const bidangLemah = lemah.map(namaBidangTanpaPredikat);
  return {
    kekuatan: kuat.length ? `${nama} menunjukkan kekuatan pada bidang ${joinDan(kuat)}.` : "",
    pendampingan: lemah.length ? `${nama} masih perlu pendampingan pada bidang ${joinDan(lemah)}.` : "",
    catatanGuru: topik.length
      ? `Pada semester ini ${nama} mengikuti layanan ${joinDan(topik)}.`
      : kuat.length || lemah.length
        ? `Perkembangan ${nama} ditinjau melalui capaian empat bidang layanan BK pada semester ini.`
        : "",
    rekomendasiOrangtua: bidangLemah.length
      ? `Orang tua diharapkan mendampingi murid menguatkan bidang ${joinDan(bidangLemah)} di rumah dengan komunikasi yang hangat.`
      : topik.length
        ? `Orang tua diharapkan mendukung penerapan hasil layanan ${joinDan(topik)} di rumah.`
        : "",
    tindakLanjut: bidangLemah.length
      ? `Guru BK akan melanjutkan pendampingan pada bidang ${joinDan(bidangLemah)} dan berkoordinasi dengan wali kelas.`
      : topik.length
        ? `Perkembangan setelah layanan ${joinDan(topik)} dipantau bersama wali kelas pada pertemuan berikutnya.`
        : kuat.length
          ? "Capaian yang sudah baik dipelihara dan diperkuat melalui layanan klasikal atau kelompok."
          : "",
  };
}

export function isiCatatanGuruKosong(state, siswaId) {
  const rec = ensureRaport(state, siswaId);
  const siswa = state.siswa.find((s) => s.id === siswaId);
  const usulan = usulanCatatanGuru(state, siswaId);
  let n = 0;
  for (const key of ["kekuatan", "pendampingan", "catatanGuru", "rekomendasiOrangtua", "tindakLanjut"]) {
    if (!String(rec[key] || "").trim() && usulan[key]) {
      rec[key] = usulan[key];
      n++;
    }
  }
  for (const p of PROFIL) {
    const pred = rec.bidang[p.dari]?.predikat || "";
    if (!pred) continue;
    if (!String(rec.profil[p.id].capaian || "").trim()) {
      rec.profil[p.id].capaian = pred;
      n++;
    }
    const capaian = rec.profil[p.id].capaian || pred;
    if (!String(rec.profil[p.id].deskripsi || "").trim() && capaian) {
      rec.profil[p.id].deskripsi = buatDeskripsiProfil(siswa?.nama, p.id, capaian);
      n++;
    }
  }
  return n;
}

export function statistik(state) {
  const tahun = state.periode.tahunAjaran;
  const semester = state.periode.semester;
  const siswa = state.siswa.filter((s) => kelasIdPada(state, s, tahun));
  let isi = 0;
  for (const s of siswa) if (raportTerisiPredikat(lihatRaport(state, s.id))) isi++;
  const layanan = state.layanan.filter((l) => l.tahunAjaran === tahun && l.semester === semester);
  return {
    siswa: siswa.length,
    kelas: kelasTerpakai(state).length,
    isi,
    layanan: layanan.length,
  };
}

export function layananUntukSiswa(state, siswaId, tahun = state.periode.tahunAjaran, semester = state.periode.semester) {
  return state.layanan
    .filter((l) => l.tahunAjaran === tahun && l.semester === semester && (l.siswaIds || []).includes(siswaId))
    .sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)));
}

function topikPrinsip(list, grup, key) {
  const topik = [];
  for (const l of list) {
    if (l.rahasia || !l[grup]?.[key]) continue;
    if (l.topik && !topik.includes(l.topik)) topik.push(l.topik);
  }
  return topik;
}

export function ringkasPrinsip(list) {
  const out = { berkesadaran: "", bermakna: "", menggembirakan: "" };
  for (const key of Object.keys(out)) {
    const topik = topikPrinsip(list, "prinsip", key);
    if (topik.length) out[key] = `Terawat melalui layanan ${joinDan(topik)}.`;
  }
  return out;
}

export function ringkasPengalaman(list) {
  const out = { memahami: "", mengaplikasi: "", merefleksi: "" };
  for (const key of Object.keys(out)) {
    const topik = topikPrinsip(list, "pengalaman", key);
    if (topik.length) out[key] = `Pengalaman ini muncul pada layanan ${joinDan(topik)}.`;
  }
  return out;
}

export function parseCsv(text) {
  const src = String(text || "").replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  const firstLine = src.split("\n")[0] || "";
  const semi = (firstLine.match(/;/g) || []).length;
  const comma = (firstLine.match(/,/g) || []).length;
  const tab = (firstLine.match(/\t/g) || []).length;
  let delim = ",";
  if (tab >= semi && tab >= comma && tab > 0) delim = "\t";
  else if (semi > comma) delim = ";";
  const rows = [];
  let row = [];
  let cur = "";
  let q = false;
  for (let i = 0; i < src.length; i++) {
    const c = src[i];
    if (q) {
      if (c === '"') {
        if (src[i + 1] === '"') {
          cur += '"';
          i++;
        } else q = false;
      } else cur += c;
    } else if (c === '"') q = true;
    else if (c === delim) {
      row.push(cur);
      cur = "";
    } else if (c === "\n") {
      row.push(cur);
      rows.push(row);
      row = [];
      cur = "";
    } else cur += c;
  }
  if (cur.length || row.length) {
    row.push(cur);
    rows.push(row);
  }
  return rows.filter((r) => r.some((cell) => String(cell).trim() !== ""));
}

function normHeader(h) {
  return String(h || "").trim().toLowerCase().replace(/\s+/g, " ");
}

function mapHeaders(headers) {
  const idx = {};
  headers.forEach((h, i) => {
    const n = normHeader(h);
    for (const [key, aliases] of Object.entries(HEADER_ALIAS)) {
      if (aliases.includes(n) && idx[key] == null) idx[key] = i;
    }
  });
  return idx;
}

function bersihTeks(v) {
  return String(v ?? "").trim().replace(/\s+/g, " ");
}

function normTanggal(v) {
  const s = bersihTeks(v);
  if (!s) return "";
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) return s.slice(0, 10);
  const m = s.match(/^(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})$/);
  if (!m) return "";
  let day = Number(m[1]);
  let month = Number(m[2]);
  let year = Number(m[3]);
  if (year < 100) year += year >= 50 ? 1900 : 2000;
  if (day <= 12 && month > 12) {
    const tukar = day;
    day = month;
    month = tukar;
  }
  if (month < 1 || month > 12 || day < 1 || day > 31) return "";
  return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

function bersihNis(v) {
  let s = bersihTeks(v);
  if (/^\d+\.0$/.test(s)) s = s.slice(0, -2);
  if (/e\+/i.test(s)) return s;
  return s;
}

export function rowsToSiswa(matrix, { kelasPaksa = "" } = {}) {
  const errors = [];
  const siswa = [];
  if (!matrix?.length) return { siswa, errors: ["Berkas kosong."] };
  const idx = mapHeaders(matrix[0]);
  if (idx.nama == null) {
    return { siswa, errors: ["Kolom nama tidak ditemukan. Gunakan judul kolom Nama pada baris pertama."] };
  }
  matrix.slice(1).forEach((r, n) => {
    const nama = bersihTeks(r[idx.nama]);
    if (!nama) return;
    const kelas = kelasPaksa || (idx.kelas != null ? normKelas(r[idx.kelas]) : "");
    if (!kelas) {
      errors.push(`Baris ${n + 2}: ${nama} belum memiliki kelas.`);
      return;
    }
    const ambil = (key) => (idx[key] != null ? bersihTeks(r[idx[key]]) : "");
    siswa.push({
      nama,
      nisn: bersihNis(idx.nisn != null ? r[idx.nisn] : ""),
      nis: bersihNis(idx.nis != null ? r[idx.nis] : ""),
      jk: normJk(ambil("jk")),
      kelas,
      noAbsen: ambil("noAbsen"),
      tempatLahir: ambil("tempatLahir"),
      tanggalLahir: normTanggal(ambil("tanggalLahir")),
      agama: ambil("agama"),
      namaAyah: ambil("namaAyah"),
      namaIbu: ambil("namaIbu"),
    });
  });
  if (!siswa.length && !errors.length) errors.push("Tidak ada nama murid yang terbaca.");
  return { siswa, errors };
}

function siswaBaru() {
  return {
    id: uid(),
    nisn: "",
    nis: "",
    nama: "",
    jk: "",
    kelasId: "",
    noAbsen: "",
    tempatLahir: "",
    tanggalLahir: "",
    agama: "",
    namaAyah: "",
    namaIbu: "",
  };
}

export function imporSiswa(state, daftar) {
  const tahun = state.periode.tahunAjaran;
  const waliLama = {};
  const nbmWaliLama = {};
  for (const kelas of state.kelas) {
    waliLama[kelas.nama] = kelas.waliKelas || "";
    nbmWaliLama[kelas.nama] = kelas.nbmWali || "";
  }
  const jumlahLama = state.siswa.length;
  state.siswa = [];
  state.penempatan = {};
  state.raport = {};
  state.kelas = [];
  for (const layanan of state.layanan || []) layanan.siswaIds = [];
  const hasil = { baru: 0, dihapus: jumlahLama, kelasBaru: [] };
  state.penempatan[tahun] = {};
  for (const row of daftar) {
    let kelas = state.kelas.find((k) => k.nama === row.kelas);
    if (!kelas) {
      kelas = {
        id: uid(),
        nama: row.kelas,
        tingkat: tingkatDari(row.kelas),
        waliKelas: waliLama[row.kelas] || "",
        nbmWali: nbmWaliLama[row.kelas] || "",
      };
      state.kelas.push(kelas);
      hasil.kelasBaru.push(row.kelas);
    }
    const siswa = siswaBaru();
    siswa.nama = row.nama;
    siswa.kelasId = kelas.id;
    state.siswa.push(siswa);
    state.penempatan[tahun][siswa.id] = kelas.id;
    for (const key of ["nisn", "nis", "jk", "noAbsen", "tempatLahir", "tanggalLahir", "agama", "namaAyah", "namaIbu"]) {
      if (String(row[key] || "").trim()) siswa[key] = row[key];
    }
    hasil.baru++;
  }
  state.kelas.sort(bandingKelas);
  return hasil;
}

export function naikNamaKelas(nama) {
  const m = String(nama || "").trim().toUpperCase().match(/^(\d+)\s*([A-Z].*)$/);
  if (!m) return { status: "tetap", nama: normKelas(nama) };
  const n = Number(m[1]);
  const suf = m[2].replace(/\s+/g, "");
  if (n >= 9) return { status: "lulus", nama: null };
  return { status: "naik", nama: `${n + 1}${suf}` };
}

export function rencanaKenaikan(state) {
  const tahun = state.periode.tahunAjaran;
  const ada = tahunPunyaPenempatan(state, tahun);
  const list = [];
  for (const s of state.siswa) {
    const kid = ada ? state.penempatan[tahun][s.id] : s.kelasId;
    if (!kid) continue;
    const k = state.kelas.find((c) => c.id === kid);
    if (!k) continue;
    const next = naikNamaKelas(k.nama);
    list.push({ siswaId: s.id, nama: s.nama, dari: k.nama, ke: next.nama, status: next.status });
  }
  return list.sort((a, b) => a.dari.localeCompare(b.dari, "id") || a.nama.localeCompare(b.nama, "id"));
}

export function terapkanKenaikan(state, tahunBaru) {
  seedPenempatan(state, state.periode.tahunAjaran);
  const items = rencanaKenaikan(state);
  const map = {};
  for (const item of items) {
    if (item.status === "lulus") continue;
    let kelas = state.kelas.find((k) => k.nama === item.ke);
    if (!kelas) {
      kelas = { id: uid(), nama: item.ke, tingkat: tingkatDari(item.ke), waliKelas: "", nbmWali: "" };
      state.kelas.push(kelas);
    }
    map[item.siswaId] = kelas.id;
    const siswa = state.siswa.find((s) => s.id === item.siswaId);
    if (siswa) siswa.kelasId = kelas.id;
  }
  state.penempatan[tahunBaru] = map;
  state.periode.tahunAjaran = tahunBaru;
  state.periode.semester = "Ganjil";
  state.kelas.sort(bandingKelas);
  return items;
}

export function buatKelas(state, nama, waliKelas = "") {
  const bersih = normKelas(nama);
  if (!bersih) return { error: "Nama kelas masih kosong." };
  if (state.kelas.some((k) => k.nama === bersih)) return { error: `Kelas ${bersih} sudah ada.` };
  const kelas = { id: uid(), nama: bersih, tingkat: tingkatDari(bersih), waliKelas: waliKelas.trim(), nbmWali: "" };
  state.kelas.push(kelas);
  state.kelas.sort(bandingKelas);
  return { kelas };
}

export function tambahSiswa(state, data) {
  const nama = bersihTeks(data.nama);
  if (!nama) return { error: "Nama murid masih kosong." };
  if (!data.kelasId) return { error: "Pilih kelas terlebih dahulu." };
  const siswa = siswaBaru();
  siswa.nama = nama;
  siswa.jk = data.jk || "";
  siswa.nisn = bersihTeks(data.nisn);
  siswa.nis = bersihTeks(data.nis);
  siswa.noAbsen = bersihTeks(data.noAbsen);
  siswa.agama = data.agama || "";
  siswa.kelasId = data.kelasId;
  state.siswa.push(siswa);
  tempatkan(state, siswa.id, data.kelasId);
  return { siswa };
}

export function hapusSiswa(state, siswaId) {
  state.siswa = state.siswa.filter((s) => s.id !== siswaId);
  for (const tahun of Object.keys(state.penempatan || {})) delete state.penempatan[tahun][siswaId];
  for (const key of Object.keys(state.raport || {})) {
    if (key.startsWith(`${siswaId}|`)) delete state.raport[key];
  }
  for (const l of state.layanan) l.siswaIds = (l.siswaIds || []).filter((id) => id !== siswaId);
}

export function kelasMasihDipakai(state, kelasId) {
  if (state.siswa.some((s) => s.kelasId === kelasId)) return true;
  return Object.values(state.penempatan || {}).some((map) => Object.values(map).includes(kelasId));
}

export const KEPALA_DEF_DF = [
  "NISN",
  "Nama",
  "Prinsip Berkesadaran",
  "Prinsip Bermakna",
  "Prinsip Menggembirakan",
  "Pengalaman Memahami",
  "Pengalaman Mengaplikasi",
  "Pengalaman Merefleksi",
  "Kekuatan",
  "Perlu Pendampingan",
  "Catatan Perkembangan",
  "Rekomendasi bagi Orang Tua",
  "Tindak Lanjut",
];

export const KEPALA_DEF_E = ["Tanggal", "Jenis", "Bidang", "Topik", "NISN sasaran", "Rahasia"];

const DEF_DF_ALIAS = {
  nisn: ["nisn"],
  nama: ["nama", "nama siswa", "nama lengkap", "nama murid"],
  berkesadaran: ["prinsip berkesadaran", "berkesadaran"],
  bermakna: ["prinsip bermakna", "bermakna"],
  menggembirakan: ["prinsip menggembirakan", "menggembirakan"],
  memahami: ["pengalaman memahami", "memahami"],
  mengaplikasi: ["pengalaman mengaplikasi", "mengaplikasi"],
  merefleksi: ["pengalaman merefleksi", "merefleksi"],
  kekuatan: ["kekuatan"],
  pendampingan: ["perlu pendampingan", "pendampingan"],
  catatanGuru: ["catatan perkembangan", "catatan guru", "catatan perkembangan untuk raport"],
  rekomendasiOrangtua: ["rekomendasi bagi orang tua", "rekomendasi orang tua", "rekomendasi"],
  tindakLanjut: ["tindak lanjut"],
};

const DEF_E_ALIAS = {
  tanggal: ["tanggal"],
  jenis: ["jenis", "jenis layanan"],
  bidang: ["bidang"],
  topik: ["topik"],
  nisn: ["nisn sasaran", "nisn", "nisn murid"],
  rahasia: ["rahasia"],
};

function indeksKolomAlias(headers, aliasMap) {
  const idx = {};
  headers.forEach((h, i) => {
    const n = normHeader(h);
    for (const [key, aliases] of Object.entries(aliasMap)) {
      if (aliases.includes(n) && idx[key] == null) idx[key] = i;
    }
  });
  return idx;
}

function cariSiswaDiKelas(state, kelasId, nisn, nama) {
  const daftar = siswaDiKelas(state, kelasId);
  const n = bersihNis(nisn);
  if (n) {
    const byNisn = daftar.find((s) => s.nisn && s.nisn === n);
    if (byNisn) return byNisn;
  }
  const nm = bersihTeks(nama).toLowerCase();
  if (!nm) return null;
  return daftar.find((s) => String(s.nama || "").trim().toLowerCase() === nm) || null;
}

export function matrixBlankoDefDf(state, kelasId) {
  const rows = [KEPALA_DEF_DF.slice()];
  for (const s of siswaDiKelas(state, kelasId)) {
    rows.push([s.nisn || "", s.nama || "", "", "", "", "", "", "", "", "", "", "", ""]);
  }
  return rows;
}

export function matrixContohDefDf(state, kelasId) {
  const rows = [KEPALA_DEF_DF.slice()];
  for (const s of siswaDiKelas(state, kelasId)) {
    const nama = s.nama || "Murid";
    rows.push([
      s.nisn || "",
      nama,
      "Murid mengikuti layanan dengan kesadaran tujuan diri.",
      "Topik layanan terhubung dengan kehidupan sehari-hari.",
      "Suasana layanan positif dan mendorong partisipasi.",
      "Murid memahami materi layanan yang diberikan.",
      "Murid mencoba menerapkan hasil layanan di kelas.",
      "Murid merefleksikan pengalaman setelah layanan.",
      `${nama} menunjukkan kekuatan pada bidang pribadi dan sosial.`,
      `${nama} masih perlu pendampingan pada kebiasaan belajar.`,
      `Pada semester ini ${nama} mengikuti layanan pengenalan potensi diri.`,
      "Orang tua diharapkan mendampingi murid dengan komunikasi yang hangat di rumah.",
      "Guru BK memantau perkembangan bersama wali kelas pada pertemuan berikutnya.",
    ]);
  }
  return rows;
}

export function matrixBlankoDefE() {
  return [
    KEPALA_DEF_E.slice(),
    ["", "Bimbingan klasikal", "pribadi", "", "", "Tidak"],
  ];
}

export function matrixContohDefE(state, kelasId) {
  const daftar = siswaDiKelas(state, kelasId);
  const contohNisn = daftar[0]?.nisn || "";
  const hari = new Date().toISOString().slice(0, 10);
  return [
    KEPALA_DEF_E.slice(),
    [hari, "Bimbingan klasikal", "pribadi", "Pengenalan potensi diri dan pengendalian emosi", "", "Tidak"],
    [hari, "Konseling individual", "sosial", "Penyesuaian diri di kelas", contohNisn, "Ya"],
  ];
}

function yaTidak(v) {
  const s = bersihTeks(v).toLowerCase();
  return ["ya", "y", "true", "1", "rahasi", "rahasia"].some((x) => s === x || s.startsWith(x));
}

function normBidangLayanan(v) {
  const s = bersihTeks(v).toLowerCase();
  if (!s) return "pribadi";
  const hit = BIDANG.find((b) => b.id === s || b.nama.toLowerCase() === s);
  return hit?.id || "pribadi";
}

function normJenisLayanan(v) {
  const s = bersihTeks(v);
  if (!s) return "Bimbingan klasikal";
  const hit = JENIS_LAYANAN.find((j) => j.toLowerCase() === s.toLowerCase());
  return hit || s;
}

export function parseLembarDefDf(matrix) {
  if (!matrix?.length) return { rows: [], errors: ["Lembar D dan F kosong."] };
  const headers = matrix[0] || [];
  const idx = indeksKolomAlias(headers, DEF_DF_ALIAS);
  if (idx.nama == null && idx.nisn == null) {
    return { rows: [], errors: ["Lembar D dan F membutuhkan kolom Nama atau NISN."] };
  }
  const rows = [];
  const errors = [];
  for (let i = 1; i < matrix.length; i++) {
    const r = matrix[i] || [];
    const ambil = (key) => (idx[key] != null ? bersihTeks(r[idx[key]]) : "");
    const nisn = bersihNis(ambil("nisn"));
    const nama = ambil("nama");
    if (!nisn && !nama) continue;
    rows.push({
      nisn,
      nama,
      prinsipCatatan: {
        berkesadaran: ambil("berkesadaran"),
        bermakna: ambil("bermakna"),
        menggembirakan: ambil("menggembirakan"),
      },
      pengalamanCatatan: {
        memahami: ambil("memahami"),
        mengaplikasi: ambil("mengaplikasi"),
        merefleksi: ambil("merefleksi"),
      },
      kekuatan: ambil("kekuatan"),
      pendampingan: ambil("pendampingan"),
      catatanGuru: ambil("catatanGuru"),
      rekomendasiOrangtua: ambil("rekomendasiOrangtua"),
      tindakLanjut: ambil("tindakLanjut"),
      baris: i + 1,
    });
  }
  return { rows, errors };
}

export function parseLembarDefE(matrix) {
  if (!matrix?.length) return { rows: [], errors: [] };
  const headers = matrix[0] || [];
  const idx = indeksKolomAlias(headers, DEF_E_ALIAS);
  if (idx.topik == null && idx.jenis == null) {
    return { rows: [], errors: ["Lembar E Layanan membutuhkan kolom Topik atau Jenis."] };
  }
  const rows = [];
  const errors = [];
  for (let i = 1; i < matrix.length; i++) {
    const r = matrix[i] || [];
    const ambil = (key) => (idx[key] != null ? bersihTeks(r[idx[key]]) : "");
    const topik = ambil("topik");
    const jenis = ambil("jenis");
    if (!topik && !jenis) continue;
    if (!topik) {
      errors.push(`E baris ${i + 1}: topik masih kosong.`);
      continue;
    }
    rows.push({
      tanggal: normTanggal(ambil("tanggal")) || new Date().toISOString().slice(0, 10),
      jenis: normJenisLayanan(jenis),
      bidang: normBidangLayanan(ambil("bidang")),
      topik,
      nisn: bersihNis(ambil("nisn")),
      rahasia: yaTidak(ambil("rahasia")),
      baris: i + 1,
    });
  }
  return { rows, errors };
}

export const KEPALA_PREDIKAT = ["NISN", "Nama", "Absen", "Pribadi", "Sosial", "Belajar", "Karir"];

const PREDIKAT_ALIAS = {
  nisn: ["nisn"],
  nama: ["nama", "nama siswa", "nama lengkap", "nama murid"],
  noAbsen: ["absen", "no absen", "nomor absen"],
  pribadi: ["pribadi"],
  sosial: ["sosial"],
  belajar: ["belajar"],
  karir: ["karir"],
};

function normKodePredikat(v) {
  const s = bersihTeks(v).toUpperCase().replace(/\s+/g, "");
  if (!s || s === "—" || s === "-") return "";
  if (PREDIKAT.some((p) => p.id === s)) return s;
  const nama = PREDIKAT.find((p) => p.nama.toUpperCase().replace(/\s+/g, "") === s);
  return nama?.id || "";
}

export function matrixBlankoPredikat(state, kelasId) {
  const rows = [KEPALA_PREDIKAT.slice()];
  for (const s of siswaDiKelas(state, kelasId)) {
    const rec = lihatRaport(state, s.id);
    rows.push([
      s.nisn || "",
      s.nama || "",
      s.noAbsen || "",
      rec.bidang.pribadi.predikat || "",
      rec.bidang.sosial.predikat || "",
      rec.bidang.belajar.predikat || "",
      rec.bidang.karir.predikat || "",
    ]);
  }
  return rows;
}

export function matrixContohPredikat(state, kelasId) {
  const contoh = ["SB", "BSH", "MB", "BB"];
  const rows = [KEPALA_PREDIKAT.slice()];
  siswaDiKelas(state, kelasId).forEach((s, i) => {
    const a = contoh[i % 4];
    const b = contoh[(i + 1) % 4];
    rows.push([s.nisn || "", s.nama || "", s.noAbsen || "", a, b, a, b]);
  });
  return rows;
}

export function parseLembarPredikat(matrix) {
  if (!matrix?.length) return { rows: [], errors: ["Lembar predikat kosong."] };
  const idx = indeksKolomAlias(matrix[0] || [], PREDIKAT_ALIAS);
  if (idx.nama == null && idx.nisn == null) {
    return { rows: [], errors: ["Lembar predikat membutuhkan kolom Nama atau NISN."] };
  }
  const rows = [];
  const errors = [];
  for (let i = 1; i < matrix.length; i++) {
    const r = matrix[i] || [];
    const ambil = (key) => (idx[key] != null ? bersihTeks(r[idx[key]]) : "");
    const nisn = bersihNis(ambil("nisn"));
    const nama = ambil("nama");
    if (!nisn && !nama) continue;
    const predikat = {};
    for (const b of BIDANG) {
      const mentah = ambil(b.id);
      if (!mentah) {
        predikat[b.id] = "";
        continue;
      }
      const kode = normKodePredikat(mentah);
      if (!kode) {
        errors.push(`Baris ${i + 1}: predikat ${b.nama} "${mentah}" tidak dikenali. Pakai SB, BSH, MB, atau BB.`);
        continue;
      }
      predikat[b.id] = kode;
    }
    rows.push({ nisn, nama, predikat, baris: i + 1 });
  }
  return { rows, errors };
}

export function imporPredikatKelas(state, kelasId, daftar) {
  const hasil = { diperbarui: 0, gagal: [], uraian: 0 };
  for (const row of daftar) {
    const siswa = cariSiswaDiKelas(state, kelasId, row.nisn, row.nama);
    if (!siswa) {
      hasil.gagal.push(`Baris ${row.baris}: murid ${row.nama || row.nisn || "—"} tidak ada di kelas ini.`);
      continue;
    }
    const rec = ensureRaport(state, siswa.id);
    let ubah = false;
    for (const b of BIDANG) {
      const kode = row.predikat[b.id];
      if (!kode) continue;
      if (rec.bidang[b.id].predikat !== kode) {
        rec.bidang[b.id].predikat = kode;
        ubah = true;
      }
      if (!String(rec.bidang[b.id].deskripsi || "").trim()) {
        rec.bidang[b.id].deskripsi = buatDeskripsi(siswa.nama, b.id, kode, indikatorTerpilih(rec, b.id));
        hasil.uraian++;
      }
    }
    if (ubah) hasil.diperbarui++;
  }
  return hasil;
}

export function imporDefKelas(state, kelasId, { dfRows = [], eRows = [] } = {}) {
  const hasil = { df: 0, layanan: 0, gagal: [], errors: [] };
  for (const row of dfRows) {
    const siswa = cariSiswaDiKelas(state, kelasId, row.nisn, row.nama);
    if (!siswa) {
      hasil.gagal.push(`D/F baris ${row.baris}: murid ${row.nama || row.nisn || "—"} tidak ada di kelas ini.`);
      continue;
    }
    const rec = ensureRaport(state, siswa.id);
    let ubah = false;
    for (const key of PRINSIP.map((p) => p.id)) {
      if (row.prinsipCatatan[key]) {
        rec.prinsipCatatan[key] = row.prinsipCatatan[key];
        ubah = true;
      }
    }
    for (const key of PENGALAMAN.map((p) => p.id)) {
      if (row.pengalamanCatatan[key]) {
        rec.pengalamanCatatan[key] = row.pengalamanCatatan[key];
        ubah = true;
      }
    }
    for (const key of ["kekuatan", "pendampingan", "catatanGuru", "rekomendasiOrangtua", "tindakLanjut"]) {
      if (row[key]) {
        rec[key] = row[key];
        ubah = true;
      }
    }
    if (ubah) hasil.df++;
  }
  const muridKelas = siswaDiKelas(state, kelasId);
  for (const row of eRows) {
    let ids = [];
    if (row.nisn) {
      const siswa = cariSiswaDiKelas(state, kelasId, row.nisn, "");
      if (!siswa) {
        hasil.gagal.push(`E baris ${row.baris}: NISN ${row.nisn} tidak ada di kelas ini.`);
        continue;
      }
      ids = [siswa.id];
    } else {
      ids = muridKelas.map((s) => s.id);
    }
    if (!ids.length) {
      hasil.gagal.push(`E baris ${row.baris}: kelas belum punya murid.`);
      continue;
    }
    state.layanan.unshift({
      id: uid(),
      tahunAjaran: state.periode.tahunAjaran,
      semester: state.periode.semester,
      tanggal: row.tanggal,
      jenis: row.jenis,
      bidang: row.bidang,
      sasaran: row.nisn ? "siswa" : "kelas",
      kelasId,
      siswaIds: ids,
      topik: row.topik,
      tujuan: "",
      catatan: "",
      prinsip: { berkesadaran: true, bermakna: true, menggembirakan: true },
      pengalaman: { memahami: true, mengaplikasi: true, merefleksi: true },
      dimensi: [],
      rahasia: !!row.rahasia,
    });
    hasil.layanan++;
  }
  return hasil;
}
