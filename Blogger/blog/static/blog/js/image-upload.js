document.addEventListener("DOMContentLoaded", function () {

    const imageInput = document.querySelector(
        '.native-file-field input[type="file"]'
    );

    const fileName = document.getElementById("uploadFileName");
    const previewBox = document.getElementById("imagePreviewBox");
    const preview = document.getElementById("imagePreview");

    if (!imageInput || !fileName || !previewBox || !preview) {
        return;
    }

    let previewUrl = null;

    imageInput.addEventListener("change", function () {

        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
            previewUrl = null;
        }

        const file = this.files[0];

        if (!file) {
            fileName.textContent =
                document.documentElement.lang === "ar"
                    ? "لم يتم اختيار صورة"
                    : "No image selected";

            previewBox.hidden = true;
            preview.removeAttribute("src");
            return;
        }

        fileName.textContent = file.name;

        if (file.type.startsWith("image/")) {
            previewUrl = URL.createObjectURL(file);
            preview.src = previewUrl;
            previewBox.hidden = false;
        } else {
            previewBox.hidden = true;
            preview.removeAttribute("src");
        }
    });

    window.addEventListener("beforeunload", function () {
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }
    });

});