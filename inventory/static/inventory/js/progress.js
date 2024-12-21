function updateNavbarProgressBar(data) {

    const overallProgressContainer = document.getElementById("overall-progress-container");

    if (overallProgressContainer) {
        if (data.is_active === true) {
            const overallProgressBar = document.getElementById("overall-progress-bar");
            overallProgressContainer.style.display = "block";
            if (overallProgressBar) {
                const progress = data.progress || 0;
                overallProgressBar.style.width = `${progress}%`;
                overallProgressBar.innerText = `${progress}%`;
            }
        } else {
            overallProgressContainer.style.display = "none";
        }
    }
}

function pollOverallProgress() {
    fetch("/overall-progress/")
        .then(response => response.json())
        .then(data => {
            updateNavbarProgressBar(data);
        })
        .catch(error => console.error("Error fetching overall progress:", error));
}

document.addEventListener("DOMContentLoaded", function () {
    setInterval(pollOverallProgress, 2000);
});
