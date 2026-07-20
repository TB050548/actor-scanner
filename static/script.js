function goHome() { window.location.href = "/"; }
function goToScanner() { window.location.href = "/scanner"; }
function goToSearch() { window.location.href = "/search"; }

// Auto-submit form when file is chosen
document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("imageInput");
    const form = document.getElementById("uploadForm");
    if (input && form) {
        input.addEventListener("change", function () {
            if (input.files.length > 0) {
                form.submit();  // automatically submits as soon as user picks a file
            }
        });
    }
});