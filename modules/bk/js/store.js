import { FILE_NAME, FOLDER_NAME, initialState, migrate } from "./model.js?v=13";

const DB_NAME = "raport-bk-smpm22";
const LS_CLIENT = "raportbk.googleClientId";

export const status = {
  saving: false,
  folder: "none",
  folderName: "",
  folderError: "",
  google: "off",
  googleEmail: "",
  googleName: "",
  googleError: "",
  lastLocal: null,
  lastFolder: null,
  lastCloud: null,
};

let db = null;
let state = initialState();
let dirHandle = null;
let saveTimer = null;
let cloudTimer = null;
let googleToken = "";
let googleExpiry = 0;
let onStatus = () => {};

export function setStatusListener(fn) {
  onStatus = fn;
}

export function getState() {
  return state;
}

export function getClientId() {
  return localStorage.getItem(LS_CLIENT) || "";
}

export function setClientId(id) {
  localStorage.setItem(LS_CLIENT, String(id || "").trim());
}

function poke() {
  onStatus(status);
}

function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => {
      if (!req.result.objectStoreNames.contains("kv")) req.result.createObjectStore("kv");
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function idbGet(key) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction("kv", "readonly");
    const r = tx.objectStore("kv").get(key);
    r.onsuccess = () => resolve(r.result);
    r.onerror = () => reject(r.error);
  });
}

function idbSet(key, value) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction("kv", "readwrite");
    tx.objectStore("kv").put(value, key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function writeJson(dir, name, data) {
  const fh = await dir.getFileHandle(name, { create: true });
  const writable = await fh.createWritable();
  await writable.write(JSON.stringify(data, null, 2));
  await writable.close();
}

async function readJson(dir, name) {
  const fh = await dir.getFileHandle(name);
  const file = await fh.getFile();
  return JSON.parse(await file.text());
}

async function muatServer() {
  try {
    const res = await fetch("/bk/api/state", { headers: { Accept: "application/json" } });
    if (!res.ok) return null;
    const data = await res.json();
    if (!data || !data.meta) return null;
    return data;
  } catch {
    return null;
  }
}

export async function load() {
  db = await openDb();
  const saved = await idbGet("state");
  const remote = await muatServer();
  const localTime = saved?.meta?.updatedAt || "";
  const remoteTime = remote?.meta?.updatedAt || "";
  const pilihan = remote && remoteTime >= localTime ? remote : (saved || remote);
  state = migrate(pilihan || initialState());
  status.googleEmail = state.meta.googleEmail || "";
  status.googleName = state.meta.googleName || "";
  status.lastLocal = state.meta.updatedAt;
  dirHandle = (await idbGet("dir")) || null;
  if (dirHandle) {
    status.folderName = dirHandle.name || FOLDER_NAME;
    try {
      const perm = await dirHandle.queryPermission({ mode: "readwrite" });
      status.folder = perm === "granted" ? "saved" : "needs-permission";
    } catch {
      status.folder = "needs-permission";
    }
  }
  poke();
  return state;
}

export function replaceState(next, { renderSave = true } = {}) {
  state = migrate(next);
  status.googleEmail = state.meta.googleEmail || status.googleEmail;
  status.googleName = state.meta.googleName || status.googleName;
  if (renderSave) scheduleSave();
  return state;
}

export function touch() {
  state.meta.updatedAt = new Date().toISOString();
  status.lastLocal = state.meta.updatedAt;
  scheduleSave();
}

function scheduleSave() {
  status.saving = true;
  poke();
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    persist().catch((err) => {
      status.folderError = err.message || String(err);
      status.saving = false;
      poke();
    });
  }, 350);
}

export async function persist() {
  state.meta.updatedAt = state.meta.updatedAt || new Date().toISOString();
  await idbSet("state", state);
  status.lastLocal = state.meta.updatedAt;
  try {
    await fetch("/bk/api/state", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state),
    });
  } catch {
    /* salinan di peramban tetap ada bila MySQL belum terjangkau */
  }
  status.saving = false;
  if (dirHandle) await saveFolder();
  if (googleToken && Date.now() < googleExpiry - 60000 && state.meta.cloudFolderId) {
    clearTimeout(cloudTimer);
    cloudTimer = setTimeout(() => {
      uploadToDrive().catch((err) => {
        status.google = "error";
        status.googleError = pesanGoogle(err);
        poke();
      });
    }, 1200);
  }
  poke();
}

export async function saveFolder() {
  if (!dirHandle) return false;
  const perm = await dirHandle.queryPermission({ mode: "readwrite" });
  if (perm !== "granted") {
    status.folder = "needs-permission";
    poke();
    return false;
  }
  try {
    await writeJson(dirHandle, FILE_NAME, state);
    status.folder = "saved";
    status.folderError = "";
    status.lastFolder = new Date().toISOString();
    status.folderName = dirHandle.name || FOLDER_NAME;
    poke();
    return true;
  } catch (err) {
    status.folder = "error";
    status.folderError = err.message || String(err);
    poke();
    return false;
  }
}

export async function connectFolder() {
  if (!window.showDirectoryPicker) {
    throw new Error("Pilih folder hanya tersedia di Google Chrome atau Microsoft Edge. Buka aplikasi lewat salah satu peramban itu.");
  }
  const parent = await window.showDirectoryPicker({ mode: "readwrite", id: "raport-bk-smpm22" });
  const dir = parent.name === FOLDER_NAME ? parent : await parent.getDirectoryHandle(FOLDER_NAME, { create: true });
  dirHandle = dir;
  await idbSet("dir", dir);
  status.folderName = dir.name;
  status.folder = "saved";
  status.folderError = "";
  let remote = null;
  try {
    remote = migrate(await readJson(dir, FILE_NAME));
  } catch {
    remote = null;
  }
  if (!remote) await saveFolder();
  poke();
  return { remote, folderName: dir.name };
}

export async function ensureFolderPermission() {
  if (!dirHandle) return false;
  let perm = await dirHandle.queryPermission({ mode: "readwrite" });
  if (perm !== "granted") perm = await dirHandle.requestPermission({ mode: "readwrite" });
  status.folder = perm === "granted" ? "saved" : "needs-permission";
  if (perm === "granted") await saveFolder();
  poke();
  return perm === "granted";
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const ada = document.querySelector(`script[src="${src}"]`);
    if (ada && window.google?.accounts?.oauth2) return resolve();
    const s = document.createElement("script");
    s.src = src;
    s.async = true;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error("Gagal memuat layanan masuk Google. Periksa koneksi internet."));
    document.head.appendChild(s);
  });
}

function requestToken(clientId) {
  return new Promise(async (resolve, reject) => {
    await loadScript("https://accounts.google.com/gsi/client");
    if (!window.google?.accounts?.oauth2) {
      reject(new Error("Layanan masuk Google belum siap."));
      return;
    }
    const client = google.accounts.oauth2.initTokenClient({
      client_id: clientId,
      scope: "https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email",
      callback: (resp) => {
        if (resp.error) reject(new Error(resp.error_description || resp.error));
        else resolve(resp.access_token);
      },
      error_callback: (err) => reject(new Error(err.message || "Masuk Google dibatalkan.")),
    });
    client.requestAccessToken({ prompt: "consent" });
  });
}

async function api(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      Authorization: `Bearer ${googleToken}`,
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Google menjawab ${res.status}`);
  }
  if (res.status === 204) return null;
  const ctype = res.headers.get("content-type") || "";
  if (ctype.includes("application/json")) return res.json();
  return res.text();
}

async function ensureCloudFolder() {
  const q = encodeURIComponent(`mimeType='application/vnd.google-apps.folder' and name='${FOLDER_NAME}' and trashed=false`);
  const found = await api(`https://www.googleapis.com/drive/v3/files?q=${q}&fields=files(id,name)&pageSize=5`);
  if (found.files?.length) return found.files[0].id;
  const made = await api("https://www.googleapis.com/drive/v3/files", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: FOLDER_NAME, mimeType: "application/vnd.google-apps.folder" }),
  });
  return made.id;
}

async function findCloudFile(folderId) {
  const q = encodeURIComponent(`'${folderId}' in parents and name='${FILE_NAME}' and trashed=false`);
  const found = await api(`https://www.googleapis.com/drive/v3/files?q=${q}&fields=files(id,name,modifiedTime)&pageSize=5`);
  return found.files?.[0] || null;
}

export async function loginGoogle() {
  const clientId = getClientId();
  if (!clientId) throw new Error("Isi Client ID Google terlebih dahulu di menu Pengaturan.");
  if (!navigator.onLine) throw new Error("Tidak ada internet. Data tetap tersimpan di komputer. Masuk Google bisa dilakukan saat jaringan ada.");
  status.google = "syncing";
  status.googleError = "";
  poke();
  try {
    return await masukGoogle(clientId);
  } catch (err) {
    status.google = "error";
    status.googleError = pesanGoogle(err);
    googleToken = "";
    poke();
    throw new Error(status.googleError);
  }
}

async function masukGoogle(clientId) {
  googleToken = await requestToken(clientId);
  googleExpiry = Date.now() + 50 * 60 * 1000;
  const profile = await api("https://www.googleapis.com/oauth2/v3/userinfo");
  status.google = "on";
  status.googleEmail = profile.email || "";
  status.googleName = profile.name || "";
  state.meta.googleEmail = status.googleEmail;
  state.meta.googleName = status.googleName;
  if (!state.guru.email) state.guru.email = status.googleEmail;
  if (!state.guru.nama) state.guru.nama = status.googleName;
  const folderId = await ensureCloudFolder();
  state.meta.cloudFolderId = folderId;
  const file = await findCloudFile(folderId);
  let remote = null;
  if (file) {
    state.meta.cloudFileId = file.id;
    const text = await api(`https://www.googleapis.com/drive/v3/files/${file.id}?alt=media`);
    remote = migrate(typeof text === "string" ? JSON.parse(text) : text);
  }
  poke();
  return { remote, email: status.googleEmail, name: status.googleName };
}

async function uploadMultipart(folderId, fileId) {
  const metadata = { name: FILE_NAME, mimeType: "application/json" };
  if (!fileId) metadata.parents = [folderId];
  const boundary = `raportbk${Date.now()}`;
  const body =
    `--${boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n${JSON.stringify(metadata)}\r\n` +
    `--${boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n${JSON.stringify(state)}\r\n` +
    `--${boundary}--`;
  const url = fileId
    ? `https://www.googleapis.com/upload/drive/v3/files/${fileId}?uploadType=multipart`
    : "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart";
  return api(url, {
    method: fileId ? "PATCH" : "POST",
    headers: { "Content-Type": `multipart/related; boundary=${boundary}` },
    body,
  });
}

export async function uploadToDrive() {
  if (!googleToken) throw new Error("Masuk dengan akun Google terlebih dahulu.");
  status.google = "syncing";
  poke();
  const folderId = state.meta.cloudFolderId || (await ensureCloudFolder());
  state.meta.cloudFolderId = folderId;
  const uploaded = await uploadMultipart(folderId, state.meta.cloudFileId);
  if (uploaded?.id) state.meta.cloudFileId = uploaded.id;
  status.google = "on";
  status.googleError = "";
  status.lastCloud = new Date().toISOString();
  await idbSet("state", state);
  poke();
  return uploaded;
}

export async function downloadFromDrive() {
  if (!googleToken) throw new Error("Masuk dengan akun Google terlebih dahulu.");
  const folderId = state.meta.cloudFolderId || (await ensureCloudFolder());
  state.meta.cloudFolderId = folderId;
  const file = await findCloudFile(folderId);
  if (!file) throw new Error("Belum ada berkas raport di Google Drive akun ini.");
  state.meta.cloudFileId = file.id;
  const text = await api(`https://www.googleapis.com/drive/v3/files/${file.id}?alt=media`);
  return migrate(typeof text === "string" ? JSON.parse(text) : text);
}

function pesanGoogle(err) {
  const raw = err.message || String(err);
  if (raw.includes("accessNotConfigured") || raw.includes("accessNotConfigured")) return "Google Drive API belum diaktifkan pada project Client ID.";
  if (raw.includes("redirect_uri") || raw.includes("origin")) return "Origin aplikasi belum didaftarkan. Tambahkan http://127.0.0.1:8787 pada OAuth Client ID.";
  if (raw.length > 280) return "Google menolak permintaan. Periksa Client ID, Drive API, dan origin http://127.0.0.1:8787.";
  return raw;
}

export function jelaskanStatus() {
  const bagian = [];
  if (!navigator.onLine) bagian.push("Offline");
  if (status.saving) bagian.push("Menyimpan di komputer…");
  else if (status.lastLocal) bagian.push("Tersimpan di komputer");
  else bagian.push("Belum ada simpanan");
  if (status.folder === "saved") bagian.push(`Folder Drive: ${status.folderName}`);
  else if (status.folder === "needs-permission") bagian.push("Folder Drive perlu izin ulang");
  else if (status.folder === "error") bagian.push("Folder Drive gagal ditulis");
  else bagian.push("Folder Drive belum disambungkan");
  if (status.google === "on") bagian.push(status.googleEmail || "Google tersambung");
  else if (status.google === "syncing") bagian.push("Mengunggah ke Google Drive…");
  else if (status.google === "error") bagian.push("Unggah Google tertunda");
  else if (status.googleEmail) bagian.push(`Akun terakhir ${status.googleEmail}`);
  return bagian.join(" · ");
}
