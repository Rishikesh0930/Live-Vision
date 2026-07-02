document.addEventListener("DOMContentLoaded", function () {

    const errorBox = document.getElementById("errorMessage");
    const inputs = document.querySelectorAll("input");

    inputs.forEach(input => {
        input.addEventListener("input", () => {
            if (errorBox && errorBox.style.display !== "none") {
                errorBox.style.display = "none";
            }
        });
    });

});