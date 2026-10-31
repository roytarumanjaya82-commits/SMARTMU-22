import { tampilan } from "./views.js?v=13";
import {
  bandingKelas,
  buatDeskripsi,
  buatKelas,
  deepSet,
  ensureRaport,
  hapusSiswa,
  imporDefKelas,
  imporPredikatKelas,
  imporSiswa,
  matrixBlankoDefDf,
  matrixBlankoDefE,
  matrixBlankoPredikat,
  matrixContohDefDf,
  matrixContohDefE,
  matrixContohPredikat,
  parseLembarDefDf,
  parseLembarDefE,
  parseLembarPredikat,
  indikatorTerpilih,
  isiCatatanGuruKosong,
  isiDeskripsiKosong,
  isiProfilDariBidang,
  kelasIdPada,
  kelasMasihDipakai,
  migrate,
  namaPredikat,
  normKelas,
  parseCsv,
  raportTerisiPredikat,
  rapikanNama,
  rencanaKenaikan,
  rowsToSiswa,
  siswaDiKelas,
  statistik,
  susunUlangBidang,
  tambahSiswa,
  tempatkan,
  terapkanKenaikan,
  tahunBerikutnya,
  uid,
} from "./model.js?v=13";
import {
  connectFolder,
  downloadFromDrive,
  ensureFolderPermission,
  getClientId,
  getState,
  jelaskanStatus,
  loginGoogle,
  persist,
  replaceState,
  saveFolder,
  setClientId,
  setStatusListener,
  status,
  load,
  touch,
  uploadToDrive,
} from "./store.js?v=13";

const appEl = document.getElementById("app");
const ui = {
  kelasId: "",
  siswaId: "",
  tabRaport: "siswa",
  detailId: "",
  preview: null,
  draftLayanan: null,
  kenaikan: null,
  modal: null,
  tanggalCetak: new Date().toISOString().slice(0, 10),
  cetakMode: "siswa",
  lengkap: false,
  showKelasForm: false,
};

let toastTimer;

function toast(pesan) {
  const el = document.getElementById("toast");
  if (!el || !pesan) return;
  el.textContent = pesan;
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 4800);
}

function routeNow() {
  const nama = location.hash.replace(/^#\/?/, "") || "beranda";
  return ["beranda", "murid", "raport", "layanan", "cetak", "pengaturan", "panduan"].includes(nama) ? nama : "beranda";
}

function paintStatus() {
  const el = document.getElementById("status-line");
  if (el) el.textContent = jelaskanStatus();
}

function rapikanPilihan() {
  const state = getState();
  const kelas = state.kelas.slice().sort(bandingKelas);
  if (!kelas.some((k) => k.id === ui.kelasId)) ui.kelasId = kelas[0]?.id || "";
  const daftar = ui.kelasId ? siswaDiKelas(state, ui.kelasId) : [];
  if (!daftar.some((s) => s.id === ui.siswaId)) ui.siswaId = daftar[0]?.id || "";
}

function render() {
  rapikanPilihan();
  document.title = "Raport BK · SMP Muhammadiyah 22 Setiabudi Pamulang";
  appEl.innerHTML = tampilan(getState(), ui, routeNow());
  paintStatus();
}

function renderKeep() {
  const y = document.querySelector(".main")?.scrollTop || 0;
  render();
  const main = document.querySelector(".main");
  if (main) main.scrollTop = y;
}

function pergi(route) {
  const next = `#/${route}`;
  if (location.hash === next) render();
  else location.hash = next;
}

function adaIsi(data) {
  return data.siswa.length > 0 || data.kelas.length > 0 || data.layanan.length > 0 || Object.keys(data.raport).length > 0;
}

function muatData(remote) {
  const lokal = getState();
  remote.meta.cloudFileId = lokal.meta.cloudFileId || remote.meta.cloudFileId;
  remote.meta.cloudFolderId = lokal.meta.cloudFolderId || remote.meta.cloudFolderId;
  remote.meta.googleEmail = status.googleEmail || lokal.meta.googleEmail || remote.meta.googleEmail;
  remote.meta.googleName = status.googleName || lokal.meta.googleName || remote.meta.googleName;
  if (!remote.guru.nama && lokal.guru.nama) remote.guru.nama = lokal.guru.nama;
  if (!remote.guru.email) remote.guru.email = status.googleEmail || lokal.guru.email || "";
  replaceState(remote);
  ui.kelasId = "";
  ui.siswaId = "";
  ui.modal = null;
  render();
}

async function setelahRemote(remote, sumber) {
  if (!remote) {
    if (sumber === "Google Drive" && adaIsi(getState())) {
      try { await uploadToDrive(); } catch { /* tombol unggah tetap tersedia */ }
    }
    toast(sumber === "Google Drive" ? "Akun Google tersambung. Belum ada berkas raport di Drive." : "Folder Google Drive tersambung.");
    render();
    return;
  }
  if (!adaIsi(getState())) {
    muatData(remote);
    toast(`Data dimuat dari ${sumber}.`);
    return;
  }
  if (!adaIsi(remote)) {
    toast(`${sumber} masih kosong. Data yang sedang terbuka tetap dipakai.`);
    if (sumber === "Google Drive") {
      try { await uploadToDrive(); } catch { /* disimpan lokal */ }
    }
    if (sumber.startsWith("folder")) {
      try { await saveFolder(); } catch { /* status folder menampilkan kendala */ }
    }
    render();
    return;
  }
  ui.modal = { jenis: "konflik", sumber, remote, lokalUpdated: getState().meta.updatedAt };
  render();
}

function tulis(el) {
  if (!(el instanceof HTMLElement)) return false;
  const state = getState();
  const nilai = el.type === "checkbox" ? el.checked : el.value;
  if (el.dataset.bind) {
    deepSet(state, el.dataset.bind, nilai);
    touch();
    return "bind";
  }
  if (el.dataset.raport) {
    const rec = ensureRaport(state, el.dataset.raport);
    deepSet(rec, el.dataset.field, nilai);
    touch();
    return "raport";
  }
  if (el.dataset.siswa) {
    const siswa = state.siswa.find((s) => s.id === el.dataset.siswa);
    if (!siswa) return false;
    deepSet(siswa, el.dataset.field, nilai);
    touch();
    return "siswa";
  }
  if (el.dataset.kelas) {
    const kelas = state.kelas.find((k) => k.id === el.dataset.kelas);
    if (!kelas) return false;
    deepSet(kelas, el.dataset.field, nilai);
    touch();
    return "kelas";
  }
  if (el.dataset.draft && ui.draftLayanan) {
    deepSet(ui.draftLayanan, el.dataset.draft, nilai);
    if (el.dataset.draft === "rahasia") ui.draftLayanan._rahasiaManual = true;
    return "draft";
  }
  return false;
}

function lengkapiPredikat(el) {
  const bidang = el.dataset.field.split(".")[1];
  const rec = ensureRaport(getState(), el.dataset.raport);
  const siswa = getState().siswa.find((s) => s.id === el.dataset.raport);
  const item = rec.bidang[bidang];
  if (item?.predikat && !item.deskripsi.trim()) {
    item.deskripsi = buatDeskripsi(siswa?.nama, bidang, item.predikat, indikatorTerpilih(rec, bidang));
  }
}

function terapkanPredikat(siswaId, bidang, nilai) {
  const state = getState();
  const siswa = state.siswa.find((s) => s.id === siswaId);
  const rec = ensureRaport(state, siswaId);
  rec.bidang[bidang].predikat = nilai;
  if (nilai && !rec.bidang[bidang].deskripsi.trim()) {
    rec.bidang[bidang].deskripsi = buatDeskripsi(siswa?.nama, bidang, nilai, indikatorTerpilih(rec, bidang));
    const ta = document.querySelector(`textarea[data-raport="${siswaId}"][data-field="bidang.${bidang}.deskripsi"]`);
    if (ta && !ta.value.trim()) ta.value = rec.bidang[bidang].deskripsi;
  }
  touch();
  document.querySelectorAll(`.seg-btn[data-siswa="${siswaId}"][data-bidang="${bidang}"]`).forEach((tombol) => {
    tombol.classList.toggle("on", tombol.dataset.nilai === nilai);
  });
  const nama = document.querySelector(`.seg-btn[data-siswa="${siswaId}"][data-bidang="${bidang}"]`)?.parentElement?.parentElement?.querySelector(".pred-nama");
  if (nama) nama.textContent = namaPredikat(nilai) || "Belum dipilih";
  document.querySelector(`[data-dot="${siswaId}"]`)?.classList.toggle("done", raportTerisiPredikat(rec));
}

function layananKosong() {
  return {
    id: "",
    tanggal: new Date().toISOString().slice(0, 10),
    jenis: "Bimbingan klasikal",
    bidang: "pribadi",
    sasaran: "kelas",
    kelasId: ui.kelasId || "",
    siswaIds: [],
    topik: "",
    tujuan: "",
    catatan: "",
    prinsip: { berkesadaran: false, bermakna: false, menggembirakan: false },
    pengalaman: { memahami: false, mengaplikasi: false, merefleksi: false },
    dimensi: [],
    rahasia: false,
    _rahasiaManual: false,
  };
}

function bukaDraft(asal) {
  const dasar = layananKosong();
  if (!asal) return dasar;
  return {
    ...dasar,
    ...asal,
    prinsip: { ...dasar.prinsip, ...(asal.prinsip || {}) },
    pengalaman: { ...dasar.pengalaman, ...(asal.pengalaman || {}) },
    dimensi: [...(asal.dimensi || [])],
    siswaIds: [...(asal.siswaIds || [])],
    _rahasiaManual: true,
  };
}

function namaSheetLayak(sheet) {
  if (!sheet || sheet === "CSV" || /^sheet\d+$/i.test(sheet)) return "";
  return normKelas(sheet);
}

function gabungLembar(lembar) {
  const siswa = [];
  const errors = [];
  for (const { sheet, matrix } of lembar) {
    if (!matrix?.length) continue;
    const pertama = rowsToSiswa(matrix, {});
    if (pertama.errors.some((e) => e.includes("Kolom nama"))) {
      errors.push(...pertama.errors.map((e) => `${sheet}: ${e}`));
      continue;
    }
    const paksa = namaSheetLayak(sheet);
    if (!pertama.siswa.length && paksa) {
      const ulang = rowsToSiswa(matrix, { kelasPaksa: paksa });
      siswa.push(...ulang.siswa);
      errors.push(...ulang.errors.map((e) => `${sheet}: ${e}`));
    } else {
      siswa.push(...pertama.siswa);
      errors.push(...pertama.errors.map((e) => (lembar.length > 1 ? `${sheet}: ${e}` : e)));
    }
  }
  return { siswa, errors };
}

async function bacaBerkas(file) {
  const name = file.name.toLowerCase();
  if (name.endsWith(".csv") || name.endsWith(".txt")) {
    return [{ sheet: "CSV", matrix: parseCsv(await file.text()) }];
  }
  if (!window.XLSX) throw new Error("Pustaka Excel gagal dimuat. Simpan berkas sebagai CSV lalu unggah lagi.");
  const wb = XLSX.read(await file.arrayBuffer(), { type: "array", cellDates: true });
  return wb.SheetNames.map((sheet) => ({
    sheet,
    matrix: XLSX.utils.sheet_to_json(wb.Sheets[sheet], { header: 1, raw: false, defval: "", dateNF: "yyyy-mm-dd" }),
  }));
}

async function prosesImpor(file) {
  if (!file) return;
  const input = document.getElementById("berkas-murid");
  if (input) input.value = "";
  const hasil = gabungLembar(await bacaBerkas(file));
  ui.preview = { ...hasil, fileName: file.name };
  render();
  if (!hasil.siswa.length) toast("Tidak ada murid yang terbaca. Periksa baris judul kolom.");
}

function unduhTemplate() {
  if (!window.XLSX) return toast("Pustaka Excel gagal dimuat.");
  const kepala = ["NISN", "NIS", "Nama", "Jenis Kelamin", "Kelas", "No Absen", "Tempat Lahir", "Tanggal Lahir", "Agama", "Nama Ayah", "Nama Ibu"];
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet([
    kepala,
    ["1234567890", "26001", "Nama Lengkap", "L", "7A", "1", "Pamulang", "2013-05-02", "Islam", "Nama Ayah", "Nama Ibu"],
  ]), "7A");
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet([
    kepala,
    ["1234567891", "26002", "Nama Kedua", "P", "7B", "1", "Pamulang", "2013-08-17", "Islam", "Nama Ayah", "Nama Ibu"],
  ]), "7B");
  XLSX.writeFile(wb, "template-daftar-murid-smpm22.xlsx");
}

function kelasTerpilihAtauToast() {
  const state = getState();
  const kelas = state.kelas.find((k) => k.id === ui.kelasId);
  if (!kelas) {
    toast("Pilih kelas terlebih dahulu.");
    return null;
  }
  if (!siswaDiKelas(state, kelas.id).length) {
    toast(`Kelas ${kelas.nama} belum memiliki murid.`);
    return null;
  }
  return kelas;
}

function unduhBlankoPredikat(contoh = false) {
  if (!window.XLSX) return toast("Pustaka Excel gagal dimuat.");
  const kelas = kelasTerpilihAtauToast();
  if (!kelas) return;
  const state = getState();
  const wb = XLSX.utils.book_new();
  const matrix = contoh ? matrixContohPredikat(state, kelas.id) : matrixBlankoPredikat(state, kelas.id);
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(matrix), "Predikat");
  const label = contoh ? "contoh" : "blanko";
  XLSX.writeFile(wb, `${label}-predikat-kelas-${kelas.nama.replace(/\s+/g, "")}.xlsx`);
  toast(contoh ? `Contoh predikat kelas ${kelas.nama} diunduh.` : `Blanko predikat kelas ${kelas.nama} diunduh.`);
}

async function prosesImporPredikat(file) {
  if (!file) return;
  const input = document.getElementById("berkas-predikat");
  if (input) input.value = "";
  const kelas = kelasTerpilihAtauToast();
  if (!kelas) return;
  if (!window.XLSX) throw new Error("Pustaka Excel gagal dimuat.");
  const lembar = await bacaBerkas(file);
  const matrix = lembar.find((l) => /^predikat$/i.test(String(l.sheet || "").trim()))?.matrix || lembar[0]?.matrix;
  const parsed = parseLembarPredikat(matrix || []);
  if (!parsed.rows.length) {
    toast(parsed.errors[0] || "Tidak ada predikat yang terbaca.");
    return;
  }
  const state = getState();
  const hasil = imporPredikatKelas(state, kelas.id, parsed.rows);
  touch();
  await persist();
  render();
  const gagal = [...hasil.gagal, ...parsed.errors].slice(0, 2).join(" ");
  toast(
    `Kelas ${kelas.nama}: ${hasil.diperbarui} murid diperbarui, ${hasil.uraian} uraian kosong disusun.${gagal ? ` ${gagal}` : ""}`
  );
}

function unduhBlankoDef(contoh = false) {
  if (!window.XLSX) return toast("Pustaka Excel gagal dimuat.");
  const kelas = kelasTerpilihAtauToast();
  if (!kelas) return;
  const state = getState();
  const wb = XLSX.utils.book_new();
  const df = contoh ? matrixContohDefDf(state, kelas.id) : matrixBlankoDefDf(state, kelas.id);
  const e = contoh ? matrixContohDefE(state, kelas.id) : matrixBlankoDefE();
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(df), "D dan F");
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(e), "E Layanan");
  const label = contoh ? "contoh" : "blanko";
  XLSX.writeFile(wb, `${label}-poin-DEF-kelas-${kelas.nama.replace(/\s+/g, "")}.xlsx`);
  toast(contoh ? `Contoh pengisian kelas ${kelas.nama} diunduh.` : `Blanko kelas ${kelas.nama} diunduh.`);
}

function namaLembarDef(sheet) {
  const n = String(sheet || "").trim().toLowerCase();
  if (/^d\b|d dan f|poin d|catatan d|prinsip|pengalaman|tindak/.test(n) || n === "d dan f") return "df";
  if (/^e\b|layanan|partisipasi|poin e/.test(n) || n === "e layanan") return "e";
  return "";
}

async function prosesImporDef(file) {
  if (!file) return;
  const input = document.getElementById("berkas-def");
  if (input) input.value = "";
  const kelas = kelasTerpilihAtauToast();
  if (!kelas) return;
  if (!window.XLSX) throw new Error("Pustaka Excel gagal dimuat.");
  const lembar = await bacaBerkas(file);
  let dfMatrix = null;
  let eMatrix = null;
  for (const { sheet, matrix } of lembar) {
    const jenis = namaLembarDef(sheet);
    if (jenis === "df") dfMatrix = matrix;
    else if (jenis === "e") eMatrix = matrix;
  }
  if (!dfMatrix && !eMatrix && lembar[0]) {
    const headers = (lembar[0].matrix?.[0] || []).map((h) => String(h || "").toLowerCase()).join(" ");
    if (/prinsip|pengalaman|kekuatan|tindak/.test(headers)) dfMatrix = lembar[0].matrix;
    else if (/topik|jenis/.test(headers)) eMatrix = lembar[0].matrix;
  }
  const df = dfMatrix ? parseLembarDefDf(dfMatrix) : { rows: [], errors: [] };
  const e = eMatrix ? parseLembarDefE(eMatrix) : { rows: [], errors: [] };
  const errors = [...df.errors, ...e.errors];
  if (!df.rows.length && !e.rows.length) {
    toast(errors[0] || "Berkas tidak berisi data poin D, E, atau F yang terbaca. Pakai blanko dengan lembar “D dan F” dan/atau “E Layanan”.");
    return;
  }
  const state = getState();
  const hasil = imporDefKelas(state, kelas.id, { dfRows: df.rows, eRows: e.rows });
  touch();
  await persist();
  render();
  const gagal = [...hasil.gagal, ...errors].slice(0, 3).join(" ");
  toast(
    `Kelas ${kelas.nama}: ${hasil.df} murid diperbarui (D/F), ${hasil.layanan} layanan ditambahkan (E).${gagal ? ` ${gagal}` : ""}`
  );
}

function unduhJson() {
  const blob = new Blob([JSON.stringify(getState(), null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `cadangan-raport-bk-${String(getState().periode.tahunAjaran).replace("/", "-")}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}

async function simpanLayanan() {
  const d = ui.draftLayanan;
  if (!d) return;
  if (!d.topik.trim()) return toast("Isi topik layanan.");
  if (!d.kelasId) return toast("Pilih kelas.");
  const state = getState();
  let ids = [...d.siswaIds];
  if (d.sasaran === "kelas") ids = siswaDiKelas(state, d.kelasId).map((s) => s.id);
  if (!ids.length) return toast("Sasaran layanan belum memiliki murid.");
  const rec = {
    id: d.id || uid(),
    tahunAjaran: state.periode.tahunAjaran,
    semester: state.periode.semester,
    tanggal: d.tanggal,
    jenis: d.jenis,
    bidang: d.bidang,
    sasaran: d.sasaran,
    kelasId: d.kelasId,
    siswaIds: ids,
    topik: d.topik.trim(),
    tujuan: d.tujuan.trim(),
    catatan: d.catatan.trim(),
    prinsip: { ...d.prinsip },
    pengalaman: { ...d.pengalaman },
    dimensi: [...d.dimensi],
    rahasia: !!d.rahasia,
  };
  const index = state.layanan.findIndex((l) => l.id === rec.id);
  if (index >= 0) state.layanan[index] = rec;
  else state.layanan.unshift(rec);
  ui.draftLayanan = null;
  touch();
  render();
  toast("Layanan tersimpan.");
}

async function jalankan(act, btn) {
  const state = getState();
  if (act === "sambung-folder") {
    const hasil = await connectFolder();
    await setelahRemote(hasil.remote, "folder Google Drive");
    return;
  }
  if (act === "izin-folder") {
    const boleh = await ensureFolderPermission();
    toast(boleh ? "Folder Google Drive diizinkan kembali." : "Izin folder belum diberikan.");
    render();
    return;
  }
  if (act === "masuk-google") {
    if (!getClientId()) {
      pergi("pengaturan");
      toast("Isi Client ID Google terlebih dahulu. Langkahnya ada di Pengaturan.");
      return;
    }
    toast("Membuka masuk Google…");
    const hasil = await loginGoogle();
    await setelahRemote(hasil.remote, "Google Drive");
    toast(`Masuk sebagai ${hasil.email}.`);
    return;
  }
  if (act === "unggah-google") {
    await uploadToDrive();
    toast("Data terunggah ke Google Drive.");
    render();
    return;
  }
  if (act === "muat-google") {
    const remote = await downloadFromDrive();
    await setelahRemote(remote, "Google Drive");
    return;
  }
  if (act === "simpan-client") {
    const id = document.getElementById("client-id")?.value.trim() || "";
    if (id && !id.endsWith(".apps.googleusercontent.com")) {
      toast("Client ID biasanya diakhiri apps.googleusercontent.com.");
      return;
    }
    setClientId(id);
    toast(id ? "Client ID disimpan di komputer ini." : "Client ID dikosongkan.");
    return;
  }
  if (act === "unduh-template") return unduhTemplate();
  if (act === "unduh-blanko-def") return unduhBlankoDef(false);
  if (act === "unduh-contoh-def") return unduhBlankoDef(true);
  if (act === "unduh-blanko-predikat") return unduhBlankoPredikat(false);
  if (act === "unduh-contoh-predikat") return unduhBlankoPredikat(true);
  if (act === "unduh-json") return unduhJson();
  if (act === "pilih-berkas") return document.getElementById("berkas-murid")?.click();
  if (act === "pilih-berkas-def") return document.getElementById("berkas-def")?.click();
  if (act === "pilih-berkas-predikat") return document.getElementById("berkas-predikat")?.click();
  if (act === "pilih-json") return document.getElementById("berkas-json")?.click();
  if (act === "impor-batal") {
    ui.preview = null;
    render();
    return;
  }
  if (act === "impor-ya" && ui.preview) {
    const hasil = imporSiswa(state, ui.preview.siswa);
    ui.preview = null;
    ui.detailId = "";
    ui.kelasId = "";
    ui.siswaId = "";
    touch();
    await persist();
    const st = statistik(state);
    render();
    toast(`Daftar diperbarui: ${st.kelas} kelas, ${st.siswa} murid. ${hasil.dihapus} murid lama dihapus.`);
    return;
  }
  if (act === "buka-kelas") {
    ui.showKelasForm = !ui.showKelasForm;
    renderKeep();
    return;
  }
  if (act === "simpan-kelas") {
    const hasil = buatKelas(state, document.getElementById("kelas-baru")?.value || "", document.getElementById("wali-baru")?.value || "");
    if (hasil.error) return toast(hasil.error);
    ui.kelasId = hasil.kelas.id;
    ui.showKelasForm = false;
    touch();
    render();
    toast(`Kelas ${hasil.kelas.nama} ditambahkan.`);
    return;
  }
  if (act === "pilih-kelas") {
    ui.kelasId = btn.dataset.id;
    ui.siswaId = "";
    ui.detailId = "";
    render();
    return;
  }
  if (act === "tambah-siswa") {
    const hasil = tambahSiswa(state, {
      nama: document.getElementById("baru-nama")?.value || "",
      jk: document.getElementById("baru-jk")?.value || "",
      nisn: document.getElementById("baru-nisn")?.value || "",
      kelasId: ui.kelasId,
    });
    if (hasil.error) return toast(hasil.error);
    ui.siswaId = hasil.siswa.id;
    touch();
    render();
    toast("Murid ditambahkan.");
    return;
  }
  if (act === "detail-siswa") {
    ui.detailId = ui.detailId === btn.dataset.id ? "" : btn.dataset.id;
    renderKeep();
    return;
  }
  if (act === "hapus-siswa") {
    const siswa = state.siswa.find((s) => s.id === btn.dataset.id);
    if (!siswa) return;
    if (!confirm(`Hapus ${siswa.nama} beserta raportnya?`)) return;
    hapusSiswa(state, siswa.id);
    if (ui.siswaId === siswa.id) ui.siswaId = "";
    touch();
    render();
    return;
  }
  if (act === "hapus-kelas") {
    if (kelasMasihDipakai(state, btn.dataset.id)) return toast("Kelas masih memiliki murid. Pindahkan atau hapus murid terlebih dahulu.");
    const kelas = state.kelas.find((k) => k.id === btn.dataset.id);
    if (!kelas || !confirm(`Hapus kelas ${kelas.nama}?`)) return;
    state.kelas = state.kelas.filter((k) => k.id !== kelas.id);
    ui.kelasId = "";
    touch();
    render();
    return;
  }
  if (act === "rapikan-nama") {
    let n = 0;
    for (const siswa of siswaDiKelas(state, ui.kelasId)) {
      const rapi = rapikanNama(siswa.nama);
      if (rapi && rapi !== siswa.nama) n += 1;
      if (rapi) siswa.nama = rapi;
    }
    touch();
    render();
    toast(n ? `${n} nama dirapikan.` : "Penulisan nama sudah rapi.");
    return;
  }
  if (act === "tab-raport") {
    ui.tabRaport = btn.dataset.tab;
    render();
    return;
  }
  if (act === "pilih-siswa") {
    ui.siswaId = btn.dataset.id;
    render();
    return;
  }
  if (act === "geser") {
    const daftar = siswaDiKelas(state, ui.kelasId);
    const index = daftar.findIndex((s) => s.id === ui.siswaId);
    const berikut = daftar[index + Number(btn.dataset.arah)];
    if (!berikut) return;
    ui.siswaId = berikut.id;
    render();
    return;
  }
  if (act === "predikat") {
    terapkanPredikat(btn.dataset.siswa, btn.dataset.bidang, btn.dataset.nilai);
    return;
  }
  if (act === "kosong-predikat") {
    const rec = ensureRaport(state, btn.dataset.siswa);
    rec.bidang[btn.dataset.bidang].predikat = "";
    touch();
    renderKeep();
    return;
  }
  if (act === "susun-bidang") {
    const ta = document.querySelector(`textarea[data-raport="${btn.dataset.siswa}"][data-field="bidang.${btn.dataset.bidang}.deskripsi"]`);
    if (ta?.value.trim() && !confirm("Ganti uraian yang sudah ditulis?")) return;
    if (!susunUlangBidang(state, btn.dataset.siswa, btn.dataset.bidang)) return toast("Pilih predikat terlebih dahulu.");
    if (ta) ta.value = ensureRaport(state, btn.dataset.siswa).bidang[btn.dataset.bidang].deskripsi;
    touch();
    toast("Uraian disusun.");
    return;
  }
  if (act === "susun-kelas") {
    let n = 0;
    for (const siswa of siswaDiKelas(state, ui.kelasId)) n += isiDeskripsiKosong(state, siswa.id);
    touch();
    renderKeep();
    toast(n ? `${n} uraian kosong terisi.` : "Tidak ada uraian kosong yang bisa disusun. Isi predikat terlebih dahulu.");
    return;
  }
  if (act === "isi-profil") {
    if (!confirm("Capaian profil lulusan diisi dari bidang layanan. Uraian yang masih kosong ikut terisi. Lanjutkan?")) return;
    isiProfilDariBidang(state, btn.dataset.siswa);
    touch();
    renderKeep();
    toast("Capaian profil diisi. Silakan tinjau kembali.");
    return;
  }
  if (act === "isi-catatan-guru") {
    const n = isiCatatanGuruKosong(state, btn.dataset.siswa);
    touch();
    renderKeep();
    toast(n ? `${n} kolom kosong terisi. Silakan tinjau kembali.` : "Tidak ada kolom kosong yang bisa disusun. Isi predikat bidang atau catat layanan terlebih dahulu.");
    return;
  }
  if (act === "cetak-siswa") {
    ui.cetakMode = "siswa";
    ui.siswaId = btn.dataset.id;
    const siswa = state.siswa.find((s) => s.id === btn.dataset.id);
    ui.kelasId = siswa ? kelasIdPada(state, siswa) : ui.kelasId;
    pergi("cetak");
    return;
  }
  if (act === "mode-cetak") {
    ui.cetakMode = btn.dataset.mode;
    render();
    return;
  }
  if (act === "cetak-sekarang") {
    await persist();
    window.print();
    return;
  }
  if (act === "baru-layanan") {
    ui.draftLayanan = ui.draftLayanan ? null : layananKosong();
    render();
    return;
  }
  if (act === "batal-layanan") {
    ui.draftLayanan = null;
    render();
    return;
  }
  if (act === "simpan-layanan") return simpanLayanan();
  if (act === "ubah-layanan") {
    const layanan = state.layanan.find((l) => l.id === btn.dataset.id);
    if (!layanan) return;
    ui.draftLayanan = bukaDraft(layanan);
    render();
    return;
  }
  if (act === "hapus-layanan") {
    const layanan = state.layanan.find((l) => l.id === btn.dataset.id);
    if (!layanan || !confirm(`Hapus layanan "${layanan.topik}"?`)) return;
    state.layanan = state.layanan.filter((l) => l.id !== layanan.id);
    touch();
    render();
    return;
  }
  if (act === "pilih-semua" && ui.draftLayanan) {
    ui.draftLayanan.siswaIds = siswaDiKelas(state, ui.draftLayanan.kelasId).map((s) => s.id);
    renderKeep();
    return;
  }
  if (act === "kenaikan-lihat") {
    const tahun = tahunBerikutnya(state.periode.tahunAjaran);
    ui.kenaikan = { tahunBaru: tahun, items: rencanaKenaikan(state) };
    renderKeep();
    if (!ui.kenaikan.items.length) toast("Belum ada murid yang bisa dinaikkan.");
    return;
  }
  if (act === "kenaikan-batal") {
    ui.kenaikan = null;
    renderKeep();
    return;
  }
  if (act === "kenaikan-ya") {
    const tahun = document.getElementById("tahun-baru")?.value.trim() || "";
    if (!/^\d{4}\/\d{4}$/.test(tahun)) return toast("Tulis tahun ajaran seperti 2027/2028.");
    terapkanKenaikan(state, tahun);
    ui.kenaikan = null;
    ui.kelasId = "";
    touch();
    render();
    toast(`Daftar murid dipindah ke ${tahun} semester Ganjil. Tingkat 9 tidak ikut karena sudah lulus.`);
    return;
  }
  if (act === "hapus-data") {
    ui.modal = { jenis: "hapus" };
    render();
    return;
  }
  if (act === "tutup-modal") {
    ui.modal = null;
    render();
    return;
  }
  if (act === "hapus-ya") {
    if (document.getElementById("wipe-text")?.value.trim() !== "HAPUS") return toast("Ketik HAPUS untuk melanjutkan.");
    state.siswa = [];
    state.kelas = [];
    state.layanan = [];
    state.raport = {};
    state.penempatan = {};
    ui.modal = null;
    ui.kelasId = "";
    ui.siswaId = "";
    ui.draftLayanan = null;
    touch();
    render();
    toast("Daftar murid dan raport di komputer ini sudah dihapus.");
    return;
  }
  if (act === "pakai-remote" && ui.modal?.remote) {
    const sumber = ui.modal.sumber;
    muatData(ui.modal.remote);
    toast(`Data ${sumber} dipakai.`);
    return;
  }
  if (act === "pakai-lokal" && ui.modal) {
    const sumber = ui.modal.sumber;
    ui.modal = null;
    render();
    if (sumber === "Google Drive") {
      try { await uploadToDrive(); } catch (err) { toast(err.message); return; }
    }
    if (String(sumber).startsWith("folder")) {
      try { await saveFolder(); } catch (err) { toast(err.message); return; }
    }
    toast("Data yang sedang terbuka tetap dipakai.");
  }
}

function onInput(e) {
  const el = e.target;
  if (el.id === "cari-murid") {
    const q = el.value.trim().toLowerCase();
    document.querySelectorAll("#tabel-murid tbody tr[data-cari]").forEach((baris) => {
      baris.hidden = !!q && !baris.dataset.cari.includes(q);
    });
    return;
  }
  tulis(el);
}

function onChange(e) {
  const el = e.target;
  if (el.id === "berkas-murid") {
    prosesImpor(el.files?.[0]).catch((err) => toast(err.message));
    return;
  }
  if (el.id === "berkas-def") {
    prosesImporDef(el.files?.[0]).catch((err) => toast(err.message));
    return;
  }
  if (el.id === "berkas-predikat") {
    prosesImporPredikat(el.files?.[0]).catch((err) => toast(err.message));
    return;
  }
  if (el.id === "berkas-json") {
    const file = el.files?.[0];
    el.value = "";
    if (!file) return;
    file.text().then((teks) => {
      const data = migrate(JSON.parse(teks));
      if (!Array.isArray(data.siswa)) throw new Error("Berkas bukan cadangan raport BK.");
      ui.modal = { jenis: "konflik", sumber: "berkas cadangan", remote: data, lokalUpdated: getState().meta.updatedAt };
      render();
    }).catch(() => toast("Berkas cadangan tidak dapat dibaca."));
    return;
  }
  if (el.id === "tanggal-cetak") {
    ui.tanggalCetak = el.value;
    renderKeep();
    return;
  }
  if (el.dataset.ui) {
    ui[el.dataset.ui] = el.value;
    if (el.dataset.ui === "kelasId") ui.siswaId = "";
    render();
    return;
  }
  if (el.dataset.uiCek) {
    ui[el.dataset.uiCek] = el.checked;
    renderKeep();
    return;
  }
  if (el.dataset.dim && ui.draftLayanan) {
    const id = el.dataset.dim;
    if (el.checked && !ui.draftLayanan.dimensi.includes(id)) ui.draftLayanan.dimensi.push(id);
    if (!el.checked) ui.draftLayanan.dimensi = ui.draftLayanan.dimensi.filter((x) => x !== id);
    return;
  }
  if (el.dataset.pick && ui.draftLayanan) {
    const id = el.dataset.pick;
    if (el.checked && !ui.draftLayanan.siswaIds.includes(id)) ui.draftLayanan.siswaIds.push(id);
    if (!el.checked) ui.draftLayanan.siswaIds = ui.draftLayanan.siswaIds.filter((x) => x !== id);
    return;
  }
  const jenis = tulis(el);
  if (jenis === "raport" && el.dataset.field?.endsWith(".predikat")) lengkapiPredikat(el);
  if (el.dataset.draft === "jenis" && ui.draftLayanan && /individual|kunjungan rumah/i.test(el.value) && !ui.draftLayanan._rahasiaManual) {
    ui.draftLayanan.rahasia = true;
    const kotak = document.querySelector('[data-draft="rahasia"]');
    if (kotak) kotak.checked = true;
  }
  if (el.dataset.render) render();
  else if (el.dataset.draft === "sasaran" || el.dataset.draft === "kelasId") renderKeep();
  else if (jenis === "siswa" && el.dataset.field === "kelasId") {
    tempatkan(getState(), el.dataset.siswa, el.value);
    touch();
    renderKeep();
  }
}

appEl.addEventListener("click", (e) => {
  const garis = e.target.closest("[data-menu-hp]");
  if (garis) {
    const sisi = garis.closest("aside");
    const buka = sisi.classList.toggle("menu-buka");
    garis.setAttribute("aria-expanded", buka ? "true" : "false");
    garis.setAttribute("aria-label", buka ? "Tutup menu" : "Buka menu");
    return;
  }
  if (e.target.closest("aside nav a")) {
    e.target.closest("aside")?.classList.remove("menu-buka");
  }
  if (e.target.classList?.contains("modal")) {
    ui.modal = null;
    render();
    return;
  }
  const btn = e.target.closest("[data-act]");
  if (!btn) return;
  jalankan(btn.dataset.act, btn).catch((err) => toast(err.message || "Terjadi kendala."));
});
appEl.addEventListener("input", onInput);
appEl.addEventListener("change", onChange);
appEl.addEventListener("dragover", (e) => {
  const zona = e.target.closest?.("#zona-impor, #zona-def, #zona-predikat");
  if (!zona) return;
  e.preventDefault();
  zona.classList.add("over");
});
appEl.addEventListener("dragleave", (e) => {
  e.target.closest?.("#zona-impor, #zona-def, #zona-predikat")?.classList.remove("over");
});
appEl.addEventListener("drop", (e) => {
  const zona = e.target.closest?.("#zona-impor, #zona-def, #zona-predikat");
  if (!zona) return;
  e.preventDefault();
  zona.classList.remove("over");
  const file = e.dataTransfer?.files?.[0];
  if (zona.id === "zona-def") prosesImporDef(file).catch((err) => toast(err.message));
  else if (zona.id === "zona-predikat") prosesImporPredikat(file).catch((err) => toast(err.message));
  else prosesImpor(file).catch((err) => toast(err.message));
});
window.addEventListener("hashchange", render);
window.addEventListener("online", paintStatus);
window.addEventListener("offline", paintStatus);
let judulSebelumCetak = "";
window.addEventListener("beforeprint", () => {
  persist();
  judulSebelumCetak = document.title;
  document.title = " ";
});
window.addEventListener("afterprint", () => {
  if (judulSebelumCetak) document.title = judulSebelumCetak;
});
window.addEventListener("pagehide", () => { persist(); });

setStatusListener(paintStatus);
try {
  await load();
  if (!location.hash) location.replace("#/beranda");
  else render();
} catch (err) {
  appEl.textContent = `Penyimpanan peramban tidak dapat dibuka. ${err.message || err}`;
}
