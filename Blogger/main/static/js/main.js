// Header: glass effect after scrolling
const header = document.getElementById("siteHeader");
// (the nav strip gets "scrolled" once the big masthead has moved out of view)
const onScroll = () => header && header.classList.toggle("scrolled", window.scrollY > header.offsetTop - 5 && window.scrollY > 10);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

// Reveal elements on scroll
const revealEls = document.querySelectorAll(".reveal");
if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealEls.forEach((el) => io.observe(el));
} else {
  revealEls.forEach((el) => el.classList.add("in"));
}

// Post cards: golden spotlight follows the mouse + "read more" toggle
document.querySelectorAll(".post-card").forEach((card) => {
  card.addEventListener("mousemove", (e) => {
    const r = card.getBoundingClientRect();
    card.style.setProperty("--mx", `${e.clientX - r.left}px`);
    card.style.setProperty("--my", `${e.clientY - r.top}px`);
  });

  const content = card.querySelector(".post-content");
  const btn = card.querySelector(".read-more");
  if (!content || !btn) return;

  // hide the button when the text is short enough to fit (re-check once fonts load and on resize)
  const checkOverflow = () => {
    if (card.classList.contains("expanded")) return;
    btn.hidden = content.scrollHeight <= content.clientHeight + 2;
  };
  checkOverflow();
  if (document.fonts) document.fonts.ready.then(checkOverflow);
  window.addEventListener("load", checkOverflow);
  window.addEventListener("resize", checkOverflow);

  btn.addEventListener("click", () => {
    const expanded = card.classList.toggle("expanded");
    btn.querySelector(".label").textContent = expanded ? "Show less" : "Read more";
    btn.setAttribute("aria-expanded", expanded);
  });
});

// Editor: live character / word counters
const counters = document.querySelectorAll("[data-count-for]");
counters.forEach((counter) => {
  const field = document.getElementById(counter.dataset.countFor);
  if (!field) return;
  const mode = counter.dataset.mode || "chars";
  const update = () => {
    const value = field.value.trim();
    if (mode === "words") {
      const words = value ? value.split(/\s+/).length : 0;
      const minutes = Math.max(1, Math.ceil(words / 200));
      counter.textContent = `${words} words · ${minutes} min read`;
    } else {
      counter.textContent = `${field.value.length} / ${field.maxLength}`;
    }
  };
  field.addEventListener("input", update);
  update();
});

// Editor: auto-grow textarea
document.querySelectorAll("textarea.input-content").forEach((ta) => {
  const grow = () => {
    ta.style.height = "auto";
    ta.style.height = `${ta.scrollHeight}px`;
  };
  ta.addEventListener("input", grow);
});

// Intro curtain: mark as seen so it only plays once per session
try {
  if (document.documentElement.classList.contains("show-intro")) {
    sessionStorage.setItem("introSeen", "1");
    setTimeout(() => document.documentElement.classList.remove("show-intro"), 2600);
  }
} catch (e) {}

// Scroll progress bar + back-to-top button
const progress = document.getElementById("scrollProgress");
const toTop = document.getElementById("toTop");
const onScrollExtras = () => {
  const max = document.documentElement.scrollHeight - window.innerHeight;
  const p = max > 0 ? window.scrollY / max : 0;
  if (progress) progress.style.setProperty("--p", p.toFixed(4));
  if (toTop) toTop.classList.toggle("show", window.scrollY > 600);
};
window.addEventListener("scroll", onScrollExtras, { passive: true });
onScrollExtras();
if (toTop) toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

// Featured card: subtle 3D tilt (desktop pointers only)
if (window.matchMedia("(hover: hover) and (pointer: fine)").matches &&
    !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  document.querySelectorAll("[data-tilt]").forEach((el) => {
    el.addEventListener("mousemove", (e) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      el.style.transform = `perspective(1400px) rotateX(${(-y * 4).toFixed(2)}deg) rotateY(${(x * 4).toFixed(2)}deg)`;
    });
    el.addEventListener("mouseleave", () => { el.style.transform = ""; });
  });
}

// Editor: live preview of the post card
const titleInput = document.getElementById("title");
const contentInput = document.getElementById("content");
const publishInput = document.getElementById("is_published");
const previewTitle = document.getElementById("previewTitle");
const previewContent = document.getElementById("previewContent");
const previewRead = document.getElementById("previewRead");
const previewStatus = document.getElementById("previewStatus");

if (titleInput && contentInput && previewTitle && previewContent) {
  const setText = (el, value) => {
    const empty = !value.trim();
    el.textContent = empty ? el.dataset.empty : value; // textContent keeps it safe from HTML injection
    el.classList.toggle("is-empty", empty);
  };
  const statusDate = previewStatus ? previewStatus.textContent.split("·").pop().trim() : "";

  const updatePreview = () => {
    setText(previewTitle, titleInput.value);
    setText(previewContent, contentInput.value);
    const words = contentInput.value.trim() ? contentInput.value.trim().split(/\s+/).length : 0;
    if (previewRead) previewRead.textContent = `${Math.max(1, Math.ceil(words / 200))} min read`;
    if (previewStatus && publishInput) {
      previewStatus.textContent = `${publishInput.checked ? "Publishing" : "Draft"} · ${statusDate}`;
    }
  };

  [titleInput, contentInput].forEach((el) => el.addEventListener("input", updatePreview));
  if (publishInput) publishInput.addEventListener("change", updatePreview);
  updatePreview();
}
