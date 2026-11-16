/* main.js — قائمة الجوال، إغلاق التنبيهات، «اقرأ المقال كاملاً»، وعدّاد أحرف العنوان */
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

  /* المقالات الطويلة في الشبكة تُطوى، وزر يفتحها (أحدث مقال يظهر كاملاً دائماً) */
  function setupCollapse() {
    document.querySelectorAll(".post:not(.post--featured) [data-collapsible]").forEach(function (box) {
      var btn = box.parentElement.querySelector("[data-expand]");
      box.classList.add("is-collapsed");
      if (box.scrollHeight <= box.clientHeight + 4) {   /* النص قصير: لا داعي للطي */
        box.classList.remove("is-collapsed");
        return;
      }
      btn.hidden = false;
      btn.addEventListener("click", function () {
        var collapsed = box.classList.toggle("is-collapsed");
        btn.firstChild.textContent = collapsed ? "اقرأ المقال كاملاً " : "إخفاء ";
      });
    });
  }
  /* نقيس بعد تحميل الخطوط حتى يكون ارتفاع النص صحيحاً */
  if (document.fonts && document.fonts.ready) { document.fonts.ready.then(setupCollapse); } else { setupCollapse(); }

  /* عدّاد أحرف العنوان (الحد 2048) */
  document.querySelectorAll("[data-count-for]").forEach(function (counter) {
    var input = document.getElementById(counter.getAttribute("data-count-for"));
    if (!input) return;
    var update = function () { counter.textContent = input.value.length + " / 2048"; };
    input.addEventListener("input", update);
    update();
  });
})();
