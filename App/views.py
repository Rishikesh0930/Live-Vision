from django.shortcuts import render, get_object_or_404, redirect
from django.http import StreamingHttpResponse, JsonResponse
from ultralytics import YOLO
import cv2
import numpy as np
from django.conf import settings
import os
import time
from .models import Video
from django.utils import timezone
import json

def start(request):
    return render(request, 'start.html')

def home(request):
    return render(request, 'home.html')

def live_stream(request):
    return render(request, 'livestream.html')

def about(request):
    json_file_about = os.path.join(settings.BASE_DIR, 'static/json/about.json')
    with open(json_file_about, 'r', encoding='utf-8') as f:
        about = json.load(f)
    return render(request, 'about.html', {"about": about})

def video(request):
    # Sync existing videos
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


model = YOLO("yolov8n.pt")
streaming = False
recording = False
out = None
current_filename = None

# Global variables for object tracking
object_counts = {}

def draw_rounded_box(img, top_left, bottom_right, color, radius=4):
    ...

def generate_frames():
    global streaming, recording, out
    cap = cv2.VideoCapture(0)
    last_time = time.time()
    fps = 30

    while streaming: 
        current_time = time.time()
        if current_time - last_time < 1/fps:
            continue  # Skip frame to maintain FPS

        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)

        # Collect all detections for this frame
        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                detections.append((label, x1, y1, x2, y2))

        # Group by label and assign IDs
        label_counts = {}
        for detection in detections:
            label = detection[0]
            if label not in label_counts:
                label_counts[label] = 0
            label_counts[label] += 1

        # Reset counts for this frame
        current_frame_counts = label_counts.copy()

        # Draw detections with IDs
        label_counters = {}
        for label, x1, y1, x2, y2 in detections:
            if label not in label_counters:
                label_counters[label] = 0
            label_counters[label] += 1
            object_id = label_counters[label]

            cx = int((x1 + x2) / 2)
            cy = int(y1)

            # 🔹 Bounding Box (Frame)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)  # Green box

            # 🔹 Label with ID
            display_label = f"{label} {object_id}"

            # 🔹 Label Background (Rounded Box)
            font_scale = 0.6
            font_thickness = 1
            (tw, th), _ = cv2.getTextSize(display_label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            padding_x, padding_y = 20, 15

            rect_x1 = cx - (tw // 2) - padding_x
            rect_y1 = cy - th - 35
            rect_x2 = cx + (tw // 2) + padding_x
            rect_y2 = cy - 10

            draw_rounded_box(frame, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 200, 0), radius=4)

            # 🔹 Text Centered
            text_x = rect_x1 + (rect_x2 - rect_x1 - tw) // 2
            text_y = rect_y1 + (rect_y2 - rect_y1 + th) // 2
            cv2.putText(frame, display_label, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 125, 0), font_thickness, cv2.LINE_AA)

            # 🔹 Arrow pointing to object
            arrow_points = np.array([
                [cx - 10, rect_y2],
                [cx + 10, rect_y2],
                [cx, rect_y2 + 12]
            ], np.int32)
            cv2.fillPoly(frame, [arrow_points], (0, 200, 0))

        # Update global counts
        global object_counts
        object_counts = current_frame_counts

        # 🔹 Save to file if recording
        if recording and out is not None:
            out.write(frame)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        last_time = current_time

    cap.release()
    if out:
        out.release()
        out = None


def video_feed(request):
    global streaming
    streaming = True
    return StreamingHttpResponse(generate_frames(),
                content_type='multipart/x-mixed-replace; boundary=frame')


# 🔹 Start Stream
def start_stream(request):
    global streaming, recording, out, object_counts

    streaming = True
    recording = True

    # Reset object tracking for new session
    object_counts = {}

    folder = settings.MEDIA_ROOT
    os.makedirs(folder, exist_ok=True)

    filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
    save_path = os.path.join(folder, filename)

    cam = cv2.VideoCapture(0)
    width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 30  # Standard FPS
    print(f"Using FPS: {fps}, Width: {width}, Height: {height}")
    cam.release()

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))

    global current_filename
    current_filename = filename



# 🔹 Stop Stream
def stop_stream(request):
    global streaming, recording, out, current_filename, object_counts

    streaming = False
    recording = False

    if out:
        out.release()
        out = None

    if current_filename:
        # Create Video object
        video_path = os.path.join(settings.MEDIA_ROOT, current_filename)
        if os.path.exists(video_path):
            Video.objects.create(name=current_filename, file_path=video_path)
            print(f"Video saved: {video_path}")
        else:
            print(f"Video file not found: {video_path}")
        current_filename = None

    # Reset object tracking
    object_counts = {}

    return JsonResponse({"status": "stopped", "message": "Video saved successfully!"})


def get_object_details(request):
    global streaming, object_counts
    if streaming:
        return JsonResponse({"objects": object_counts})
    else:
        return JsonResponse({"message": "No objects found"})


def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.deleted = True
    video.deleted_at = timezone.now()
    video.save()
    return redirect('video-page')


def restore_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.deleted = False
    video.deleted_at = None
    video.save()
    return redirect('video-page')


def permanent_delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if os.path.exists(video.file_path):
        os.remove(video.file_path)
    video.delete()
    return redirect('video-page')