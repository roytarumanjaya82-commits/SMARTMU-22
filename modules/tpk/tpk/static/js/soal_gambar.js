(function () {
  function bindZone(zone) {
    var hiddenId = zone.getAttribute("data-paste-input");
    var previewId = zone.getAttribute("data-paste-preview");
    var hidden = hiddenId ? document.getElementById(hiddenId) : null;
    var preview = previewId ? document.getElementById(previewId) : null;
    if (!hidden) return;

    var field = zone.closest(".opsi-gambar-field") || zone.closest("form");
    var fileInput = field
      ? field.querySelector('input[type="file"].gambar-file-input, input[type="file"][name^="gambar"]')
      : null;

    function showPreview(dataUrl) {
      hidden.value = dataUrl;
      if (preview) {
        preview.hidden = false;
        preview.innerHTML = '<img src="' + dataUrl + '" alt="Preview gambar">';
      }
      zone.classList.add("has-image");
      zone.textContent = "Gambar siap · Ctrl+V lagi untuk ganti";
    }

    zone.addEventListener("click", function () {
      zone.focus();
    });

    zone.addEventListener("paste", function (e) {
      var items = (e.clipboardData && e.clipboardData.items) || [];
      for (var i = 0; i < items.length; i++) {
        if (items[i].type.indexOf("image") === 0) {
          e.preventDefault();
          var blob = items[i].getAsFile();
          var reader = new FileReader();
          reader.onload = function (ev) {
            showPreview(ev.target.result);
            if (fileInput) fileInput.value = "";
          };
          reader.readAsDataURL(blob);
          return;
        }
      }
    });

    if (fileInput) {
      fileInput.addEventListener("change", function () {
        if (fileInput.files && fileInput.files[0]) {
          hidden.value = "";
          if (preview) {
            preview.hidden = true;
            preview.innerHTML = "";
          }
          zone.classList.remove("has-image");
          zone.textContent = zone.getAttribute("data-label") || "Tempel gambar di sini (Ctrl+V)";
        }
      });
    }
  }

  // Zona soal utama (kompatibilitas lama)
  var mainZone = document.getElementById("pasteZone");
  if (mainZone && !mainZone.getAttribute("data-paste-input")) {
    mainZone.setAttribute("data-paste-input", "gambarPaste");
    mainZone.setAttribute("data-paste-preview", "pastePreview");
  }

  document.querySelectorAll(".paste-zone").forEach(bindZone);
})();
