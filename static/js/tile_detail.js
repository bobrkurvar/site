//document.addEventListener("DOMContentLoaded", () => {
//    const mainImage = document.getElementById("main-image");
//    const thumbs = document.querySelectorAll(".thumbnail");
//
//    thumbs.forEach(thumb => {
//        const img = thumb.querySelector(".thumbnail-image");
//
//        thumb.addEventListener("click", () => {
//            mainImage.src = img.src;
//
//            // снимаем подсветку со всех
//            document.querySelectorAll(".thumbnail").forEach(t => {
//                t.classList.remove("active-thumb");
//            });
//
//            // добавляем подсветку текущему
//            thumb.classList.add("active-thumb");
//        });
//    });
//});
const mainImage = document.getElementById("main-image");
const thumbnails = document.querySelectorAll(".thumbnail-image");


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


thumbnails.forEach((thumbnail) => {
    thumbnail.addEventListener("click", () => {
        if (!mainImage) {
            return;
        }

        mainImage.src = thumbnail.getAttribute("src");

        const fallback = thumbnail.dataset.fallback;

        if (fallback) {
            mainImage.dataset.fallback = fallback;
        } else {
            mainImage.removeAttribute("data-fallback");
        }

        document
            .querySelectorAll(".thumbnail")
            .forEach((item) => item.classList.remove("active-thumb"));

        thumbnail.parentElement.classList.add("active-thumb");
    });
});