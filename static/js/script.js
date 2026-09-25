// ========================================
// AI INTERVIEW PREPARATION
// Main JavaScript File
// ========================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("AI Interview Preparation App Loaded Successfully");

    // Button loading effect
    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton = form.querySelector(
                'button[type="submit"]'
            );

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerText = "Processing...";
            }

        });

    });

});