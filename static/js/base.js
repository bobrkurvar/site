document.addEventListener("DOMContentLoaded", () => {
    const dropdowns = document.querySelectorAll(".menu-dropdown");

    dropdowns.forEach(drop => {
        const btn = drop.querySelector(".dropdown-btn");
        const menu = drop.querySelector(".dropdown-menu");

        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            menu.classList.toggle("open");
        });
    });

    document.addEventListener("click", () => {
        document.querySelectorAll(".dropdown-menu.open")
            .forEach(m => m.classList.remove("open"));
    });
});