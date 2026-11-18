const header = document.getElementById("siteHeader");
const onScroll = () => header && header.classList.toggle("scrolled", window.scrollY > 4);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

document.querySelectorAll(".toast").forEach((toast) => {
  setTimeout(() => toast.classList.add("hide"), 3500);
  toast.addEventListener("animationend", () => {
    if (toast.classList.contains("hide")) toast.remove();
  });
});

const countWords = (text) => (text.trim() ? text.trim().split(/\s+/).length : 0);
const readMinutes = (text) => Math.max(1, Math.ceil(countWords(text) / 200));

document.querySelectorAll("[data-count-for]").forEach((counter) => {
  const field = document.getElementById(counter.dataset.countFor);
  if (!field) return;
  const update = () => {
    if (counter.dataset.mode === "words") {
      counter.textContent = `${countWords(field.value)} words · ${readMinutes(field.value)} min read`;
    } else {
      counter.textContent = `${field.value.length} / ${field.maxLength}`;
    }
  };
  field.addEventListener("input", update);
  update();
});

document.querySelectorAll(".textarea").forEach((area) => {
  const grow = () => {
    area.style.height = "auto";
    area.style.height = `${area.scrollHeight + 2}px`;
  };
  area.addEventListener("input", grow);
  grow();
});

const titleInput = document.getElementById("title");
const contentInput = document.getElementById("content");
const categoryInput = document.getElementById("category");
const publishInput = document.getElementById("is_published");
const previewTitle = document.getElementById("previewTitle");
const previewContent = document.getElementById("previewContent");

if (titleInput && contentInput && previewTitle && previewContent) {
  const previewCategory = document.getElementById("previewCategory");
  const previewStatus = document.getElementById("previewStatus");
  const previewRead = document.getElementById("previewRead");

  const setText = (el, value) => {
    const empty = !value.trim();
    el.textContent = empty ? el.dataset.empty : value;
    el.classList.toggle("is-empty", empty);
  };

  const updatePreview = () => {
    setText(previewTitle, titleInput.value);
    setText(previewContent, contentInput.value);
    if (previewRead) previewRead.textContent = `${readMinutes(contentInput.value)} min read`;
    if (previewCategory && categoryInput) previewCategory.textContent = categoryInput.selectedOptions[0].textContent;
    if (previewStatus && publishInput) previewStatus.hidden = publishInput.checked;
  };

  [titleInput, contentInput].forEach((el) => el.addEventListener("input", updatePreview));
  [categoryInput, publishInput].forEach((el) => el && el.addEventListener("change", updatePreview));
  updatePreview();

  const imageInput = document.getElementById("image");
  const previewImage = document.getElementById("previewImage");
  const placeholder = document.getElementById("previewPlaceholder");
  const removeImage = document.getElementById("remove_image");
  const fileName = document.getElementById("fileName");

  if (imageInput && previewImage) {
    const originalSrc = previewImage.getAttribute("src");

    const updateImagePreview = () => {
      const file = imageInput.files[0];
      if (previewImage.src.startsWith("blob:")) URL.revokeObjectURL(previewImage.src);
      if (file) {
        previewImage.src = URL.createObjectURL(file);
      } else if (originalSrc && !(removeImage && removeImage.checked)) {
        previewImage.src = originalSrc;
      } else {
        previewImage.removeAttribute("src");
      }
      const hasImage = Boolean(previewImage.getAttribute("src"));
      previewImage.hidden = !hasImage;
      if (placeholder) placeholder.hidden = hasImage;
      if (fileName) fileName.textContent = file ? file.name : "Choose an image";
    };

    imageInput.addEventListener("change", updateImagePreview);
    if (removeImage) removeImage.addEventListener("change", updateImagePreview);
  }
}
