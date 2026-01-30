const slides = document.querySelectorAll(".slide");
const dots = document.querySelectorAll(".dot");
const prevBtn = document.querySelector(".prev");
const nextBtn = document.querySelector(".next");
const sliderContainer = document.getElementById("slider-container");
let index = 0;
let interval = setInterval(nextSlide, 4000);

function showSlide(i) {
    slides.forEach((slide, idx) => {
        slide.classList.toggle("active", idx === i);
        dots[idx].classList.toggle("active", idx === i);
    });
}
function nextSlide() {
    index = (index + 1) % slides.length;
    showSlide(index);
}
function prevSlide() {
    index = (index - 1 + slides.length) % slides.length;
    showSlide(index);
}
nextBtn.addEventListener("click", () => {
    nextSlide();
    resetInterval();
});
prevBtn.addEventListener("click", () => {
    prevSlide();
    resetInterval();
});
dots.forEach((dot, i) => {
    dot.addEventListener("click", () => {
        index = i;
        showSlide(index);
        resetInterval();
    });
});
function resetInterval() {
    clearInterval(interval);
    interval = setInterval(nextSlide, 4000);
}

const darkToggle = document.getElementById('darkModeToggle');
const lightToggle = document.getElementById('lightModeToggle');

darkToggle.addEventListener('change', () => {
    if (darkToggle.checked) lightToggle.checked = false;
});

lightToggle.addEventListener('change', () => {
    if (lightToggle.checked) darkToggle.checked = false;
});