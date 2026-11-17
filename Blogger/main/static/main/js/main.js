/* main.js — قائمة الجوال، إغلاق التنبيهات، اختصار المقالات الطويلة، معاينة الصورة، وعدّاد أحرف العنوان */
(function () {
  "use strict";

  /* قائمة الجوال */
  var toggle = document.querySelector("[data-nav-toggle]");
  var links = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* إغلاق رسائل النجاح */
  document.querySelectorAll("[data-dismiss]").forEach(function (btn) {
    btn.addEventListener("click", function () { btn.closest(".alert").remove(); });
  });

  /* المقالات الطويلة في الشبكة تُختصر بتلاشٍ، ورابط «اقرأ المقال كاملاً» يفتح صفحة التفاصيل */
  function setupCollapse() {
    document.querySelectorAll(".post:not(.post--featured) [data-collapsible]").forEach(function (box) {
      box.classList.add("is-collapsed");
      if (box.scrollHeight <= box.clientHeight + 4) box.classList.remove("is-collapsed");  /* النص قصير */
    });
  }
  /* نقيس بعد تحميل الخطوط حتى يكون ارتفاع النص صحيحاً */
  if (document.fonts && document.fonts.ready) { document.fonts.ready.then(setupCollapse); } else { setupCollapse(); }

  /* حقل صورة المقال: معاينة قبل الحفظ (وفي التعديل تظهر الصورة الحالية أولاً) */
  var imageInput = document.getElementById("id_image");
  var uploadBox = document.querySelector("[data-upload]");
  if (imageInput && uploadBox) {
    var preview = uploadBox.querySelector("[data-upload-preview]");
    var empty = uploadBox.querySelector("[data-upload-empty]");
    var nameEl = document.querySelector("[data-upload-name]");
    var clearBtn = document.querySelector("[data-upload-clear]");
    var initialSrc = preview.getAttribute("data-initial-src");
    var initialName = nameEl.getAttribute("data-initial-name");

    var showImage = function () {
      var file = imageInput.files && imageInput.files[0];
      if (preview.src && preview.src.indexOf("blob:") === 0) URL.revokeObjectURL(preview.src);
      var src = file ? URL.createObjectURL(file) : initialSrc;
      if (src) { preview.src = src; } else { preview.removeAttribute("src"); }
      preview.hidden = !src;
      empty.hidden = !!src;
      uploadBox.classList.toggle("has-file", !!src);
      clearBtn.hidden = !file;
      nameEl.textContent = file ? file.name : initialName;
    };
    imageInput.addEventListener("change", showImage);
    clearBtn.addEventListener("click", function () { imageInput.value = ""; showImage(); });
    ["dragenter", "dragover"].forEach(function (e) { uploadBox.addEventListener(e, function () { uploadBox.classList.add("is-drag"); }); });
    ["dragleave", "drop"].forEach(function (e) { uploadBox.addEventListener(e, function () { uploadBox.classList.remove("is-drag"); }); });
  }

  /* عدّاد أحرف العنوان (الحد 2048) */
  document.querySelectorAll("[data-count-for]").forEach(function (counter) {
    var input = document.getElementById(counter.getAttribute("data-count-for"));
    if (!input) return;
    var update = function () { counter.textContent = input.value.length + " / 2048"; };
    input.addEventListener("input", update);
    update();
  });
})();
