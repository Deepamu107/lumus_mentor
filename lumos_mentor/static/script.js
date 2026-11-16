let questionStartTime = Date.now();
let usedHint = false;

window.addEventListener("load", () => {
    const form = document.getElementById("quiz-form");
    const timeField = document.getElementById("time_taken_sec");
    const usedHintField = document.getElementById("used_hint");
    const hintBtn = document.getElementById("hint-btn");

    if (hintBtn) {
        hintBtn.addEventListener("click", () => {
            usedHint = true;
            usedHintField.value = "true";
            alert("Hint: Focus on isolating x by reversing operations step by step.");
        });
    }

    if (form) {
        form.addEventListener("submit", () => {
            const now = Date.now();
            const diffSec = (now - questionStartTime) / 1000.0;
            timeField.value = diffSec.toFixed(2);
        });
    }
});
