(function () {
  var form = document.getElementById("formTesKelas");
  if (!form) return;

  var autosaveUrl = form.getAttribute("data-autosave-url");
  var heartbeatUrl = form.getAttribute("data-heartbeat-url");
  var saveTimer = null;
  var submitting = false;

  function collectJawaban() {
    var data = {};
    form.querySelectorAll('input[type="radio"]:checked').forEach(function (el) {
      var m = (el.name || "").match(/^soal_(\d+)$/);
      if (m) data[m[1]] = el.value;
    });
    return data;
  }

  function autosave() {
    if (!autosaveUrl || submitting) return;
    fetch(autosaveUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ jawaban: collectJawaban() }),
      credentials: "same-origin",
    }).catch(function () {});
  }

  function heartbeat(pelanggaran, alasan) {
    if (!heartbeatUrl) return;
    fetch(heartbeatUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({
        pelanggaran: !!pelanggaran,
        alasan: alasan || "",
      }),
      credentials: "same-origin",
    }).catch(function () {});
  }

  form.querySelectorAll('input[type="radio"]').forEach(function (el) {
    el.addEventListener("change", function () {
      clearTimeout(saveTimer);
      saveTimer = setTimeout(autosave, 400);
    });
  });

  form.addEventListener("submit", function () {
    submitting = true;
    autosave();
  });

  setInterval(function () {
    heartbeat(false);
  }, 15000);

  // Best-effort lock: deteksi keluar tab/aplikasi (browser tidak bisa blok OS sepenuhnya)
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) {
      heartbeat(true, "keluar tab/layar (visibility hidden)");
    }
  });
  window.addEventListener("blur", function () {
    heartbeat(true, "jendela kehilangan fokus (kemungkinan buka aplikasi lain)");
  });

  window.addEventListener("beforeunload", function (e) {
    if (submitting) return;
    autosave();
    e.preventDefault();
    e.returnValue = "";
  });

  history.pushState(null, "", location.href);
  window.addEventListener("popstate", function () {
    history.pushState(null, "", location.href);
    alert("Layar soal terkunci. Submit dulu, lalu masukkan password keluar.");
  });

  // Coba fullscreen (iOS sering menolak; Android kadang berhasil)
  try {
    var el = document.documentElement;
    if (el.requestFullscreen) el.requestFullscreen().catch(function () {});
  } catch (err) {}
})();
