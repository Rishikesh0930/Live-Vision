let timerInterval;
let detailsUpdateInterval;

function formatClock() {
    let now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    let ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12;
    hours = hours ? hours : 12;
    minutes = minutes < 10 ? "0" + minutes : minutes;
    return hours + ":" + minutes + " " + ampm;
}

function updateDetails() {
    const detailsBox = document.getElementById("detailsBox");
    const detailsContent = document.getElementById("detailsContent");

    if (detailsBox.style.display === "block") {
        fetch("/get_object_details/")
            .then(response => response.json())
            .then(data => {
                if (data.objects && Object.keys(data.objects).length > 0) {
                    let html = "<h3>Detected Objects</h3><ul>";
                    for (const [obj, count] of Object.entries(data.objects)) {
                        html += `<li><strong>${obj}:</strong> ${count}</li>`;
                    }
                    html += "</ul>";
                    detailsContent.innerHTML = html;
                } else {
                    detailsContent.innerHTML = "<p>No objects found</p>";
                }
            })
            .catch(error => {
                detailsContent.innerHTML = "<p>Error loading details</p>";
            });
    }
}

function startStream() {
    fetch("/start_stream/");  // Django URL
    const video = document.getElementById("videoStream");
    const loader = document.getElementById("loader");
    const videoText = document.getElementById("videoText");

    // Show loader, hide video & text
    loader.style.display = "flex";
    video.style.display = "none";
    videoText.style.display = "none";

    video.onload = () => {
        loader.style.display = "none";   // hide loader
        video.style.display = "block";   // show video
    };

    video.src = "/video_feed/";
    document.getElementById("liveStatus").style.display = "flex";
    document.getElementById("timer").innerText = formatClock();
    // 🔹 Update clock every second
    timerInterval = setInterval(() => {
        document.getElementById("timer").innerText = formatClock();
    }, 1000);
    // 🔹 Start button text & icon change
    document.getElementById("startBtn").innerHTML = "⏸ Streaming...";
    document.getElementById("startBtn").disabled = true; // optional: disable start button
}

function stopStream() {
    fetch("/stop_stream/"); // Django URL
    const video = document.getElementById("videoStream");
    const loader = document.getElementById("loader");
    const videoText = document.getElementById("videoText");
    // Reset to default state
    video.style.display = "none";
    loader.style.display = "none";
    videoText.style.display = "block";
    videoText.innerText = "Video Stream Will Appear Here";
    video.src = "";
    document.getElementById("liveStatus").style.display = "none";
    clearInterval(timerInterval);
    clearInterval(detailsUpdateInterval); // Stop details updates

    document.getElementById("startBtn").innerHTML = "▶ Start Stream";
    document.getElementById("startBtn").disabled = false; // optional: enable again

}

function toggleDetails() {
    const detailsBox = document.getElementById("detailsBox");

    if (detailsBox.style.display === "none") {
        // Show details
        detailsBox.style.display = "block";
        updateDetails(); // Initial update
        // Start live updates every 2 seconds
        detailsUpdateInterval = setInterval(updateDetails, 2000);
    } else {
        // Hide details
        detailsBox.style.display = "none";
        clearInterval(detailsUpdateInterval);
    }
}

function toggleMenu() {
    let menu = document.getElementById("menu");
    menu.style.display = (menu.style.display === "flex") ? "none" : "flex";
}
// Close menu if clicked outside
window.onclick = function (event) {
    if (!event.target.matches('.menu-toggle')) {
        let menu = document.getElementById("menu");
        if (menu.style.display === "flex") {
            menu.style.display = "none";
        }
    }
}