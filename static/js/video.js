function goHome() {
    window.location.href = "/home";
}
function showTab(tabName) {
    // Hide all tab contents
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    // Remove active class from buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));

    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}

function confirmDelete(videoId, videoName) {
    if (confirm(`Are you sure you want to delete "${videoName}"?`)) {
        window.location.href = `/delete_video/${videoId}/`;
    }
}

function restoreVideo(videoId) {
    window.location.href = `/restore_video/${videoId}/`;
}

function confirmPermanentDelete(videoId, videoName) {
    if (confirm(`Are you sure you want to permanently delete "${videoName}"? This action cannot be undone.`)) {
        window.location.href = `/permanent_delete_video/${videoId}/`;
    }
}