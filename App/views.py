from django.shortcuts import render, get_object_or_404, redirect
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ultralytics import YOLO
from django.conf import settings
from django.utils import timezone
from .models import Video
import numpy as np
import cv2
import os
import time
import json

model = YOLO("yolov8n.pt")
streaming = False
recording = False
video_writer = None
current_filename = None
object_counts = {}

TARGET_FPS = 20
frame_duration = 1.0 / TARGET_FPS
start_time = 0
frame_count = 0

def start(request):
    startpage_content = os.path.join(settings.BASE_DIR, 'static/json/startpage.json')
    with open(startpage_content, 'r', encoding='utf-8') as f:
        startpage = json.load(f)
    return render(request, 'start.html', {"start": startpage})

def signupPage(request):
    error = None
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmPassword = request.POST.get("confirmPassword")
        if password != confirmPassword:
            error = "Passwords do not match"
        elif User.objects.filter(username=email).exists():
            error = "User already exists"
        else:
            User.objects.create_user(username=email, email=email, password=password, first_name=name)
            return redirect("login-page")
    return render(request, 'signup.html', {"error": error})

def loginPage(request):
    error = None
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home-page")
        else:
            error = "Invalid email or password"
    return render(request, 'login.html', {"error": error})

@login_required(login_url="login-page")
def home(request):
    home_content = os.path.join(settings.BASE_DIR, 'static/json/home.json')
    with open(home_content, 'r', encoding='utf-8') as f:
        home = json.load(f)
    return render(request, 'home.html', {"home": home})

@login_required(login_url="login-page")
def live_stream(request):
    stream_content = os.path.join(settings.BASE_DIR, 'static/json/livestream.json')
    with open(stream_content, 'r', encoding='utf-8') as f:
        stream = json.load(f)
    return render(request, 'livestream.html', {"stream": stream})

@login_required(login_url="login-page")
def about(request):
    about_content = os.path.join(settings.BASE_DIR, 'static/json/about.json')
    with open(about_content, 'r', encoding='utf-8') as f:
        about = json.load(f)
    return render(request, 'about.html', {"about": about})

@login_required(login_url="login-page")
def help(request):
    return render(request, 'help.html')

@login_required(login_url="login-page")
def video(request):
    videos_dir = settings.MEDIA_ROOT
    if os.path.exists(videos_dir):
        for filename in os.listdir(videos_dir):
            if filename.endswith(('.mp4', '.avi')):
                file_path = os.path.join(videos_dir, filename)
                if not Video.objects.filter(file_path=file_path).exists():
                    Video.objects.create(name=filename, file_path=file_path)
    active_videos = Video.objects.filter(deleted=False)
    deleted_videos = Video.objects.filter(deleted=True)
    return render(request, 'video.html', {'active_videos': active_videos, 'deleted_videos': deleted_videos})

def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if os.path.exists(video.file_path):
        os.remove(video.file_path)
    video.delete()
    return redirect("video-page")


def start_stream(request):
    global streaming, recording, current_filename, video_writer, start_time, frame_count
    if streaming:
        return JsonResponse({"status": "already running"})
    streaming = True
    recording = True
    frame_count = 0
    start_time = time.time()
    folder = settings.MEDIA_ROOT
    os.makedirs(folder, exist_ok=True)
    filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
    current_filename = filename
    video_writer = None 
    return JsonResponse({"status": "started"})

def generate_frames():
    global streaming, recording, video_writer, object_counts, current_filename, start_time, frame_count
    cap = cv2.VideoCapture(0)
    frame_idx = 0
    detections = []

    while streaming:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % 2 == 0:
            results = model(frame, verbose=False)
            detections = []
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                    detections.append((label, x1, y1, x2, y2))
            
            label_counts = {}
            for d in detections:
                label_counts[d[0]] = label_counts.get(d[0], 0) + 1
            object_counts = label_counts.copy()
            
        frame_idx += 1

        label_counters = {}
        for label, x1, y1, x2, y2 in detections:
            label_counters[label] = label_counters.get(label, 0) + 1
            obj_id = label_counters[label]
            cx = int((x1 + x2) / 2)
            cy = int(y1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
            text = f"{label} {obj_id}"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            x1b = cx - (tw // 2) - 20
            y1b = cy - th - 35
            x2b = cx + (tw // 2) + 20
            y2b = cy - 10
            cv2.rectangle(frame, (x1b, y1b), (x2b, y2b), (0, 200, 0), -1)
            cv2.putText(frame, text, (x1b + 10, y1b + th + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            arrow = np.array([[cx - 10, y2b], [cx + 10, y2b], [cx, y2b + 12]])
            cv2.fillPoly(frame, [arrow], (0, 200, 0))

        if recording and current_filename:
            if video_writer is None:
                height, width, _ = frame.shape
                save_path = os.path.join(settings.MEDIA_ROOT, current_filename)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(save_path, fourcc, TARGET_FPS, (width, height))
                start_time = time.time()
                frame_count = 0

            elapsed_time = time.time() - start_time
            expected_frames = int(elapsed_time / frame_duration)
            while frame_count < expected_frames:
                video_writer.write(frame)
                frame_count += 1

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )

    cap.release()
    if video_writer:
        video_writer.release()
        video_writer = None

def video_feed(request):
    global streaming
    streaming = True
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

# def generate_frames():
#     global streaming, recording, video_writer, object_counts, current_filename, start_time, frame_count
#     cap = cv2.VideoCapture(0)
#     while streaming:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         results = model(frame, verbose=False)
#         detections = []
#         for r in results:
#             for box in r.boxes:
#                 cls_id = int(box.cls[0])
#                 label = model.names[cls_id]
#                 x1, y1, x2, y2 = box.xyxy[0].int().tolist()
#                 detections.append((label, x1, y1, x2, y2))
#         label_counts = {}
#         for d in detections:
#             label_counts[d[0]] = label_counts.get(d[0], 0) + 1
#         object_counts = label_counts.copy()
#         label_counters = {}
#         for label, x1, y1, x2, y2 in detections:
#             label_counters[label] = label_counters.get(label, 0) + 1
#             obj_id = label_counters[label]
#             cx = int((x1 + x2) / 2)
#             cy = int(y1)
#             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
#             text = f"{label} {obj_id}"
#             (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
#             x1b = cx - (tw // 2) - 20
#             y1b = cy - th - 35
#             x2b = cx + (tw // 2) + 20
#             y2b = cy - 10
#             cv2.rectangle(frame, (x1b, y1b), (x2b, y2b), (0, 200, 0), -1)
#             cv2.putText(frame, text, (x1b + 10, y1b + th + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
#             arrow = np.array([[cx - 10, y2b], [cx + 10, y2b], [cx, y2b + 12]])
#             cv2.fillPoly(frame, [arrow], (0, 200, 0))
#         if recording:
#             if video_writer is None:
#                 height, width, _ = frame.shape
#                 save_path = os.path.join(settings.MEDIA_ROOT, current_filename)
#                 fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#                 video_writer = cv2.VideoWriter(save_path, fourcc, TARGET_FPS, (width, height))
#             elapsed_time = time.time() - start_time
#             expected_frames = int(elapsed_time / frame_duration)
#             while frame_count < expected_frames:
#                 video_writer.write(frame)
#                 frame_count += 1
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()
#         yield (
#             b'--frame\r\n'
#             b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
#         )
#     cap.release()
#     if video_writer:
#         video_writer.release()
#         video_writer = None

# def video_feed(request):
#     global streaming
#     streaming = True
#     return StreamingHttpResponse(generate_frames(),content_type='multipart/x-mixed-replace; boundary=frame')

def stop_stream(request):
    global streaming, recording, video_writer, current_filename, object_counts
    streaming = False
    recording = False
    if video_writer:
        video_writer.release()
        video_writer = None
    if current_filename:
        path = os.path.join(settings.MEDIA_ROOT, current_filename)
        if os.path.exists(path):
            Video.objects.create(
                name=current_filename,
                file_path=path
            )
        current_filename = None
    object_counts = {}
    return JsonResponse({"status": "stopped"})

def get_object_details(request):
    global streaming, object_counts
    if streaming:
        return JsonResponse({"objects": object_counts})
    return JsonResponse({"objects": {}})