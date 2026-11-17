
const themeToggle = document.getElementById("theme-toggle");

function updateThemeButton() {
    const isDark =
        document.documentElement.dataset.theme === "dark";

    themeToggle.textContent = isDark ? "☀️" : "🌙";

    themeToggle.setAttribute(
        "aria-label",
        isDark ? "Switch to light mode" : "Switch to dark mode"
    );

    themeToggle.setAttribute("aria-pressed", String(isDark));
}

themeToggle.addEventListener("click", () => {
    const isDark =
        document.documentElement.dataset.theme !== "dark";

    const newTheme = isDark ? "dark" : "light";

    document.documentElement.dataset.theme = newTheme;

    localStorage.setItem("blogger-theme", newTheme);

    updateThemeButton();
});

updateThemeButton();
