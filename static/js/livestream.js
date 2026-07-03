let timerInterval;
let detailsUpdateInterval;
let dataInterval = null;
let isShowingData = false;
let streamRunning = false;   

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

function startStream() {
    streamRunning = true;
    fetch("/start_stream/");
    const video = document.getElementById("videoStream");
    const loader = document.getElementById("loader");
    const videoText = document.getElementById("videoText");
    loader.style.display = "flex";
    video.style.display = "none";
    videoText.style.display = "none";
    video.onload = () => {
        loader.style.display = "none";
        video.style.display = "block";
    };
    video.src = "/video_feed/";
    document.getElementById("liveStatus").style.display = "flex";
    document.getElementById("timer").innerText = formatClock();
    timerInterval = setInterval(() => {
        document.getElementById("timer").innerText = formatClock();
    }, 1000);
    document.getElementById("startBtn").innerHTML = "⏸ Streaming...";
    document.getElementById("startBtn").disabled = true;
}



function stopStream() {
    streamRunning = false;
    fetch("/stop_stream/");
    const video = document.getElementById("videoStream");
    const loader = document.getElementById("loader");
    const videoText = document.getElementById("videoText");
    video.style.display = "none";
    loader.style.display = "none";
    videoText.style.display = "block";
    videoText.innerText = "Video Stream Will Appear Here";
    video.src = "";
    document.getElementById("liveStatus").style.display = "none";
    clearInterval(timerInterval);
    clearInterval(detailsUpdateInterval);
    document.getElementById("startBtn").innerHTML = "▶ Start Stream";
    document.getElementById("startBtn").disabled = false;
    if (dataInterval) {
        clearInterval(dataInterval);
        dataInterval = null;
    }
    document.getElementById("liveDataContainer").style.display = "none";
    document.getElementById("showDataBtn").innerText = "Show Data";
    isShowingData = false;
}


function toggleDataDisplay() {

    const dataContainer = document.getElementById("liveDataContainer");
    const showBtn = document.getElementById("showDataBtn");
    const tableBody = document.getElementById("objectTableBody");
    if (isShowingData) {
        clearInterval(dataInterval);
        dataContainer.style.display = "none";
        showBtn.innerText = "Show Data";
        showBtn.style.backgroundColor = "";
        isShowingData = false;
        return;
    }

    dataContainer.style.display = "block";
    showBtn.innerText = "Hide Data";
    showBtn.style.backgroundColor = "#4d4d4d";
    isShowingData = true;
    if (!streamRunning) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="2"
                    style="padding:8px;text-align:center;color:#666;">
                    No Object Detected
                </td>
            </tr>
        `;
        return;
    }
    fetchLiveObjects();
    dataInterval = setInterval(fetchLiveObjects, 1000);
}


function fetchLiveObjects() {
    fetch("/get-object-details/")
    .then(response => response.json())
    .then(data => {
        const tableBody = document.getElementById("objectTableBody");
        tableBody.innerHTML = "";
        const objects = data.objects;
        if (!objects || Object.keys(objects).length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="2"
                        style="padding:8px;text-align:center;color:#666;">
                        No Object Detected
                    </td>
                </tr>
            `;
            return;
        }
        for (const [objectName, count] of Object.entries(objects)) {
            tableBody.innerHTML += `
                <tr>
                    <td style="padding:8px;font-weight:bold;text-transform:capitalize;">
                        ${objectName}
                    </td>
                    <td style="padding:8px;color:#b62f2f;font-weight:bold;">
                        ${count}
                    </td>
                </tr>
            `;
        }
    })
    .catch(error => {
        console.error(error);
        document.getElementById("objectTableBody").innerHTML = `
            <tr>
                <td colspan="2"
                    style="padding:8px;text-align:center;color:red;">
                    Error Loading Data
                </td>
            </tr>
        `;
    });
}

window.addEventListener("beforeunload", function (event) {
    if (streamRunning) {
        event.preventDefault();
        event.returnValue = "";
    }
});