function updateNavbarProgressBar(progress, visible) {
    const overallProgressContainer = document.getElementById("overall-progress-container");
    const overallProgressBar = document.getElementById("overall-progress-bar");

    if (visible) {
        overallProgressContainer.style.display = "block";
        overallProgressBar.style.width = progress + "%";
        overallProgressBar.innerText = progress + "%";
    } else {
        overallProgressContainer.style.display = "none";
    }
}

function pollOverallProgress() {
    fetch("/overall-progress/")
        .then(response => response.json())
        .then(data => {
            const progress = data.progress || 0;
            const isRunningOrPending = data.is_running_or_pending || false;

            updateNavbarProgressBar(progress, isRunningOrPending);
        })
        .catch(error => console.error("Error fetching overall progress:", error));
}

document.addEventListener("DOMContentLoaded", function () {
    setInterval(pollOverallProgress, 2000);
});
