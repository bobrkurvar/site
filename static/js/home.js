document.addEventListener("DOMContentLoaded", function () {
    const slides = document.querySelectorAll(".slide");
    const dots = document.querySelectorAll(".dot");
    const slider = document.querySelector(".slides");

    let current = 0;
    let interval = null;

    function showSlide(index) {
        slides.forEach(s => s.classList.remove("active"));
        dots.forEach(d => d.classList.remove("active"));
        slides[index].classList.add("active");
        dots[index].classList.add("active");
    }

    function nextSlide() {
        current = (current + 1) % slides.length;
        showSlide(current);
    }

    function prevSlide() {
        current = (current - 1 + slides.length) % slides.length;
        showSlide(current);
    }

    function startAutoSlide() {
        interval = setInterval(nextSlide, 4000);
    }

    function stopAutoSlide() {
        clearInterval(interval);
    }

    // Переключение по клику на левую/правую часть слайда
    slider.addEventListener("click", (e) => {
        const rect = slider.getBoundingClientRect();
        const x = e.clientX - rect.left; // координата клика внутри слайда

        stopAutoSlide();
        if (x < rect.width / 2) {
            prevSlide(); // клик слева → предыдущий слайд
        } else {
            nextSlide(); // клик справа → следующий слайд
        }
        startAutoSlide();
    });

    // Точки
    dots.forEach(dot => {
        dot.addEventListener("click", () => {
            stopAutoSlide();
            current = parseInt(dot.dataset.index);
            showSlide(current);
            startAutoSlide();
        });
    });

    // Запуск
    showSlide(current);
    startAutoSlide();
});