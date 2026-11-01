const CACHE = "presensi-smpm22-v3";
const ROOT = self.location.pathname.replace(/\/sw\.js$/, "");
const ASET = [
  ROOT + "/offline",
  ROOT + "/static/manifest.webmanifest",
  ROOT + "/static/logo_smp.jpeg",
  ROOT + "/static/icons/icon-192.png",
  ROOT + "/static/icons/icon-512.png",
  ROOT + "/static/icons/apple-touch-icon.png",
  ROOT + "/static/icons/favicon-32.png",
  ROOT + "/static/pwa.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASET)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (ROOT && url.pathname !== ROOT && !url.pathname.startsWith(ROOT + "/")) return;

  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req).catch(() => caches.match(ROOT + "/offline"))
    );
    return;
  }

  if (url.pathname.startsWith(ROOT + "/static/")) {
    event.respondWith(
      caches.match(req).then((cached) => {
        const jaringan = fetch(req)
          .then((res) => {
            if (res.ok) {
              const salinan = res.clone();
              caches.open(CACHE).then((cache) => cache.put(req, salinan));
            }
            return res;
          })
          .catch(() => cached);
        return cached || jaringan;
      })
    );
  }
});
