// Turbo and Stimulus are available globally from CDN

// Initialize Stimulus application once
const application = Stimulus.Application.start();

// Make application available globally for other scripts
window.StimulusApplication = application;

// Turbo runs automatically
// Custom configuration can go here
console.log("Turbo and Stimulus initialized");

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM ready");
});

document.addEventListener('turbo:load', function () {
    console.log('Turbo page load');
});
