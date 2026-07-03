function goHome() {
    window.location.href = "/home";
}
const answers = {
    stream: "To start the live stream, go to the 'Live Stream' page from the navigation bar and click the 'Start Stream' button. Your webcam will automatically launch and begin processing.",
    save: "When you click the 'Stop Stream' button, the video file is automatically saved into the project's 'media' folder and will immediately be listed on the 'Videos' page.",
    count: "During live streaming, the YOLOv8 model detects objects in real-time. You will see bounding boxes drawn around detected objects along with live counters visible directly on the screen.",
    delete: "On the 'Videos' page, you will find a 'Delete' button next to remove it completely from the server, click on the 'Delete' and 'Confirm' button."
};

function askBot(question, answerKey) {
    const chatBox = document.getElementById('chatBox');
    const userDiv = document.createElement('div');
    userDiv.className = 'message user-msg';
    userDiv.innerText = question;
    chatBox.appendChild(userDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    setTimeout(() => {
        const botDiv = document.createElement('div');
        botDiv.className = 'message bot-msg';
        botDiv.innerText = answers[answerKey];
        chatBox.appendChild(botDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 300);
}