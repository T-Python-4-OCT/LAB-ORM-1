
const postForm = document.querySelector(".post-form");

if (postForm) {
    const author = postForm.querySelector('[name="author"]');
    const title = postForm.querySelector('[name="title"]');
    const content = postForm.querySelector('[name="content"]');
    const image = postForm.querySelector('[name="image"]');

    const maxImageSize = 5 * 1024 * 1024;

    const allowedExtensions = [
        "jpg",
        "jpeg",
        "png",
        "webp"
    ];

    function createMessage(field) {
        const message = document.createElement("p");

        message.className = "validation-message";
        message.id = `${field.id}-validation`;
        message.setAttribute("aria-live", "polite");

        field.closest(".form-field").appendChild(message);

        const existingDescription =
            field.getAttribute("aria-describedby") || "";

        field.setAttribute(
            "aria-describedby",
            `${existingDescription} ${message.id}`.trim()
        );

        return message;
    }

    const authorMessage = createMessage(author);
    const titleMessage = createMessage(title);
    const contentMessage = createMessage(content);
    const imageMessage = createMessage(image);

    function setError(field, message, error) {
        field.setCustomValidity(error);

        field.classList.toggle("input-error", Boolean(error));

        field.setAttribute(
            "aria-invalid",
            error ? "true" : "false"
        );

        message.textContent = error;
        message.classList.remove("validation-success");

        return !error;
    }

    function validateText(field, message, minimum, maximum, label) {
        const value = field.value.trim();

        if (value.length < minimum) {
            return setError(
                field,
                message,
                `${label} must contain at least ${minimum} characters.`
            );
        }

        if (maximum && value.length > maximum) {
            return setError(
                field,
                message,
                `${label} must not exceed ${maximum} characters.`
            );
        }

        return setError(field, message, "");
    }

    function validateAuthor() {
        return validateText(
            author,
            authorMessage,
            3,
            100,
            "Author name"
        );
    }

    function validateTitle() {
        return validateText(
            title,
            titleMessage,
            5,
            2048,
            "Post title"
        );
    }

    function validateContent() {
        return validateText(
            content,
            contentMessage,
            20,
            null,
            "Your story"
        );
    }

    function validateImage() {
        const file = image.files[0];

        const uploadCard = image.closest(".upload-card");
        const uploadTitle = uploadCard.querySelector(".upload-title");
        const uploadIcon = uploadCard.querySelector(
            ".upload-icon .material-symbols-rounded"
        );

        if (!uploadTitle.dataset.originalText) {
            uploadTitle.dataset.originalText =
                uploadTitle.textContent.trim();
        }

        uploadCard.classList.remove(
            "upload-selected",
            "upload-invalid"
        );

        uploadTitle.textContent = uploadTitle.dataset.originalText;
        uploadIcon.textContent = "photo_camera";

        if (!file) {
            return setError(image, imageMessage, "");
        }

        const extension = file.name
            .split(".")
            .pop()
            .toLowerCase();

        if (!allowedExtensions.includes(extension)) {
            uploadCard.classList.add("upload-invalid");

            return setError(
                image,
                imageMessage,
                "Please select a JPG, JPEG, PNG or WebP image."
            );
        }

        if (file.size > maxImageSize) {
            uploadCard.classList.add("upload-invalid");

            return setError(
                image,
                imageMessage,
                "Image size must not exceed 5 MB."
            );
        }

        setError(image, imageMessage, "");

        uploadCard.classList.add("upload-selected");

        uploadTitle.textContent = file.name;
        uploadIcon.textContent = "check_circle";

        imageMessage.textContent =
            `Image selected — ${(file.size / (1024 * 1024)).toFixed(2)} MB`;

        imageMessage.classList.add("validation-success");

        return true;
    }

    author.addEventListener("input", validateAuthor);
    title.addEventListener("input", validateTitle);
    content.addEventListener("input", validateContent);
    image.addEventListener("change", validateImage);

    postForm.addEventListener("submit", function (event) {
        const results = [
            validateAuthor(),
            validateTitle(),
            validateContent(),
            validateImage()
        ];

        if (results.includes(false)) {
            event.preventDefault();

            postForm.reportValidity();
        }
    });
}
