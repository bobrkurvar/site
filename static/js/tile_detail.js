document.addEventListener("DOMContentLoaded", () => {
    const mainImage = document.getElementById("main-image");
    const thumbs = document.querySelectorAll(".thumbnail");

    thumbs.forEach(thumb => {
        const img = thumb.querySelector(".thumbnail-image");

        thumb.addEventListener("click", () => {
            mainImage.src = img.src;

            // снимаем подсветку со всех
            document.querySelectorAll(".thumbnail").forEach(t => {
                t.classList.remove("active-thumb");
            });

            // добавляем подсветку текущему
            thumb.classList.add("active-thumb");
        });
    });
});