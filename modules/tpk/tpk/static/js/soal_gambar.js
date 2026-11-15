(function () {
  var zone = document.getElementById("pasteZone");
  var hidden = document.getElementById("gambarPaste");
  var preview = document.getElementById("pastePreview");
  var fileInput = document.getElementById("gambarFile") || document.querySelector('input[name="gambar_file"]');
  if (!zone || !hidden) return;

  function showPreview(dataUrl) {
    hidden.value = dataUrl;
    if (!preview) return;
    preview.hidden = false;
    preview.innerHTML = '<img src="' + dataUrl + '" alt="Preview gambar soal">';
    zone.classList.add("has-image");
    zone.textContent = "Gambar siap ditempel · Ctrl+V lagi untuk ganti";
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
        zone.textContent = "Tempel gambar di sini (Ctrl+V) · Snipping Tool didukung";
      }
    });
  }
})();
