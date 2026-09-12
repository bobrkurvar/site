const filtersForm = document.getElementById("filtersForm");

if (filtersForm) {
    filtersForm.addEventListener("submit", function(event) {
        const form = event.target;
        const inputs = Array.from(form.elements);

        inputs.forEach(input => {
            if (
                (input.tagName === "INPUT" || input.tagName === "SELECT")
                && !input.value
            ) {
                input.disabled = true;
            }
        });
    });
}

document.querySelectorAll("img[data-fallback]").forEach((image) => {
    image.addEventListener("error", () => {
        const fallback = image.dataset.fallback;

        if (!fallback) {
            return;
        }

        image.removeAttribute("data-fallback");
        image.src = fallback;
    });
});