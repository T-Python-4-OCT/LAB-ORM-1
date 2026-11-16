
const translations = {

    en: {
        // Navigation
        explore: "Explore",
        write: "Write a post",

        // Homepage
        latest: "Latest Stories",
        description: "Discover the latest posts and ideas.",
        readMore: "Read More",
        noPosts: "No posts yet!",
        noPostsDescription: "Start by adding your first post.",

        // Add Post
        addHeading: "Write a New Post",
        addDescription: "Share your story with the world.",
        title: "Title",
        content: "Content",
        cover: "Cover Image",
        publish: "Publish Post",

        // Edit Post
        editHeading: "Edit Post",
        editDescription: "Update your story and save changes.",
        save: "Save Changes",

        // Post Details
        edit: "Edit Post",
        delete: "Delete Post",
        back: "Back to Posts",
        publishedOn: "Published on",

        // Common
        cancel: "Cancel",
        footerDescription: "A little space for big ideas.",

        // Placeholders
        titlePlaceholder: "Post title",
        contentPlaceholder: "Write your story here...",

        // Confirmation
        deleteConfirmation: "Are you sure you want to delete this post?",

        uploadDescription: "Choose a cover image for your post",
        chooseImage: "Choose Image",
        noImageSelected: "No image selected",
    },

    ar: {
        // Navigation
        explore: "استكشاف",
        write: "إضافة منشور",

        // Homepage
        latest: "أحدث المنشورات",
        description: "اكتشف أحدث المقالات والأفكار.",
        readMore: "قراءة المزيد",
        noPosts: "لا توجد منشورات بعد!",
        noPostsDescription: "ابدأ بإضافة منشورك الأول.",

        // Add Post
        addHeading: "كتابة منشور جديد",
        addDescription: "شارك قصتك وأفكارك مع العالم.",
        title: "العنوان",
        content: "المحتوى",
        cover: "صورة الغلاف",
        publish: "نشر المنشور",

        // Edit Post
        editHeading: "تعديل المنشور",
        editDescription: "حدّث منشورك واحفظ التغييرات.",
        save: "حفظ التعديلات",

        // Post Details
        edit: "تعديل المنشور",
        delete: "حذف المنشور",
        back: "العودة إلى المنشورات",
        publishedOn: "نُشر بتاريخ",

        // Common
        cancel: "إلغاء",
        footerDescription: "مساحة صغيرة لأفكار كبيرة.",

        // Placeholders
        titlePlaceholder: "عنوان المنشور",
        contentPlaceholder: "اكتب محتوى منشورك هنا...",

        // Confirmation
        deleteConfirmation: "هل أنت متأكد من حذف هذا المنشور؟",

        uploadDescription: "اختر صورة غلاف مناسبة لمنشورك",
        chooseImage: "اختيار صورة",
        noImageSelected: "لم يتم اختيار صورة",
    }
};


// APPLY LANGUAGE
function setLanguage(lang) {

    const selected = translations[lang] ? lang : "en";
    const dictionary = translations[selected];

    // Page language and direction
    document.documentElement.lang = selected;

    document.documentElement.dir =
        selected === "ar" ? "rtl" : "ltr";

    // Translate elements
    document.querySelectorAll("[data-i18n]").forEach(element => {

        const key = element.dataset.i18n;

        if (dictionary[key] !== undefined) {
            element.textContent = dictionary[key];
        }

    });

    // Translate title input placeholder
    const titleInput = document.getElementById("id_title");

    if (titleInput) {
        titleInput.placeholder = dictionary.titlePlaceholder;
    }

    // Update language button
    const languageButton = document.getElementById("languageToggle");

    if (languageButton) {
        languageButton.textContent =
            selected === "ar" ? "EN" : "AR";

        languageButton.setAttribute(
            "aria-label",
            selected === "ar"
                ? "Switch to English"
                : "التبديل إلى العربية"
        );
    }

    // Save user preference
    localStorage.setItem("blogger-language", selected);

    // Notify Quill and other components
    window.dispatchEvent(
        new CustomEvent("blogger:language-changed", {
            detail: {
                language: selected
            }
        })
    );
}


// INITIALIZE LANGUAGE
document.addEventListener("DOMContentLoaded", function () {

    const savedLanguage =
        localStorage.getItem("blogger-language") || "en";

    setLanguage(savedLanguage);

    const languageButton =
        document.getElementById("languageToggle");

    if (languageButton) {

        languageButton.addEventListener("click", function () {

            const current = document.documentElement.lang;

            const next = current === "ar" ? "en" : "ar";

            setLanguage(next);

        });
    }

    // Delete confirmation translation
    document.querySelectorAll("[data-confirm-delete]").forEach(form => {

        form.addEventListener("submit", function (event) {

            const current = document.documentElement.lang;

            const message =
                translations[current].deleteConfirmation;

            if (!confirm(message)) {
                event.preventDefault();
            }

        });

    });

});
