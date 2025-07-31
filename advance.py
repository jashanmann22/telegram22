from flask import Flask, request, jsonify, render_template_string
import requests
import os
import base64
import io

app = Flask(__name__)

# Set via environment variables for security
BOT_TOKEN = os.geten
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Telegram Sender</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #121212; color: #fff; display: flex; flex-direction: column; align-items: center; padding: 20px; }
        h2 { margin-bottom: 10px; }
        .card { background: #1e1e1e; padding: 20px; margin: 15px; border-radius: 15px; width: 90%; max-width: 400px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        input, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: none; font-size: 16px; }
        input { background: #2c2c2c; color: #fff; }
        button { background: #4caf50; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background: #45a049; }
        #progressContainer { display: none; width: 100%; background: #333; border-radius: 8px; margin-top: 10px; }
        #progressBar { width: 0%; height: 20px; background: #4caf50; border-radius: 8px; }
        #status { margin-top: 10px; text-align: center; }
        video { width: 100%; border-radius: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Send Text</h2>
        <input type="text" id="textMessage" placeholder="Type a message">
        <button onclick="sendText()">Send</button>
    </div>

    <div class="card">
        <h2>Send Photo</h2>
        <input type="file" id="photoInput" accept="image/*">
        <button onclick="sendPhoto()">Send Photo</button>
        <div id="progressContainer"><div id="progressBar"></div></div>
        <p id="status"></p>
    </div>

    <div class="card">
        <h2>Camera</h2>
        <video id="video" autoplay></video>
        <button onclick="capturePhoto()">Capture & Send</button>
        <div id="progressContainerCam"><div id="progressBarCam"></div></div>
        <p id="statusCam"></p>
    </div>

<script>
function sendText() {
    const message = document.getElementById('textMessage').value;
    if (!message) return alert("Please type a message.");
    fetch('/send_text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    }).then(res => res.json())
      .then(data => alert(data.status));
}

function sendPhoto() {
    const fileInput = document.getElementById('photoInput');
    if (!fileInput.files[0]) return alert("Please select a photo.");
    const formData = new FormData();
    formData.append('photo', fileInput.files[0]);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/send_photo', true);
    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            const percent = (e.loaded / e.total) * 100;
            document.getElementById('progressContainer').style.display = 'block';
            document.getElementById('progressBar').style.width = percent + '%';
        }
    };
    xhr.onload = function() {
        document.getElementById('status').innerText = xhr.status === 200 ? "Photo sent!" : "Failed.";
        setTimeout(() => {
            document.getElementById('progressContainer').style.display = 'none';
            document.getElementById('progressBar').style.width = '0%';
        }, 2000);
    };
    xhr.send(formData);
}

// Setup camera
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { document.getElementById('video').srcObject = stream; })
    .catch(err => alert("Camera access denied: " + err));

function capturePhoto() {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('photo', blob, 'camera.jpg');

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/send_photo', true);
        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                const percent = (e.loaded / e.total) * 100;
                document.getElementById('progressContainerCam').style.display = 'block';
                document.getElementById('progressBarCam').style.width = percent + '%';
            }
        };
        xhr.onload = function() {
            document.getElementById('statusCam').innerText = xhr.status === 200 ? "Camera photo sent!" : "Failed.";
            setTimeout(() => {
                document.getElementById('progressContainerCam').style.display = 'none';
                document.getElementById('progressBarCam').style.width = '0%';
            }, 2000);
        };
        xhr.send(formData);
    }, 'image/jpeg');
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/send_text', methods=['POST'])
def send_text():
    data = request.get_json()
    message = data.get('message')
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    return jsonify({"status": "Message sent!" if response.status_code == 200 else "Failed to send message."})

@app.route('/send_photo', methods=['POST'])
def send_photo():
    photo = request.files['photo']
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    files = {"photo": photo.stream}
    data = {"chat_id": CHAT_ID}
    response = requests.post(url, data=data, files=files)
    return "ok" if response.status_code == 200 else "error", response.status_code

if __name__ == '__main__':
    app.run(debug=True)
