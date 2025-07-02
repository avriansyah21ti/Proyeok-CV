# File: app.py
# --- BAGIAN IMPORT ---
from flask import Flask, render_template, Response
import cv2
import numpy as np
import math

# --- INISIALISASI APLIKASI FLASK ---
app = Flask(__name__)

# --- PENGATURAN KALIBRASI (Sama seperti kode Anda) ---
PIXELS_PER_CM = 37.0

# --- FUNGSI-FUNGSI OPENCV (Disalin langsung dari skrip Anda) ---

def get_contours(frame):
    """
    Fungsi ini mengambil frame video dan melakukan prapemrosesan untuk menemukan kontur.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    edged = cv2.Canny(blur, 50, 150)
    (contours, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        sorted_contours = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)
        return sorted_contours
    return []

def measure_object(frame, contour):
    """
    Fungsi ini mengukur kontur yang diberikan dan menggambar hasilnya pada frame.
    """
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

    # Deteksi Lingkaran
    if len(approx) > 6:
        (x, y), radius = cv2.minEnclosingCircle(contour)
        if radius > 10:
            center = (int(x), int(y))
            radius = int(radius)
            diameter = radius * 2
            diameter_cm = diameter / PIXELS_PER_CM
            circumference_cm = 2 * math.pi * radius / PIXELS_PER_CM
            
            cv2.circle(frame, center, radius, (255, 255, 0), 3)
            cv2.circle(frame, center, 4, (0, 0, 255), -1)
            cv2.putText(frame, f"D: {diameter_cm:.2f} cm", (center[0] - 60, center[1] - radius - 25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"K: {circumference_cm:.2f} cm", (center[0] - 60, center[1] - radius - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    # Deteksi Persegi Panjang
    else:
        x, y, w, h = cv2.boundingRect(contour)
        width_cm = w / PIXELS_PER_CM
        height_cm = h / PIXELS_PER_CM
        
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        centerX, centerY = x + w // 2, y + h // 2
        cv2.circle(frame, (centerX, centerY), 4, (0, 0, 255), -1)
        cv2.putText(frame, f"L: {width_cm:.2f} cm", (x, y - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"T: {height_cm:.2f} cm", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# --- FUNGSI UNTUK STREAMING VIDEO ---

def generate_frames():
    """Fungsi generator untuk streaming frame video ke web."""
    # Inisialisasi kamera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Tidak dapat membuka kamera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while True:
        # Baca frame dari kamera
        success, frame = cap.read()
        if not success:
            break
        else:
            # Lakukan pemrosesan gambar di sini (sama seperti di loop utama Anda)
            contours = get_contours(frame)
            if contours:
                for c in contours[:5]:
                    if cv2.contourArea(c) > 1000:
                        measure_object(frame, c)
            
            # Encode frame ke format JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # 'yield' frame dalam format http multipart
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    cap.release()

# --- ROUTE FLASK ---

@app.route('/')
def index():
    """Route untuk halaman utama."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Route untuk video streaming."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- MENJALANKAN APLIKASI ---

if __name__ == '__main__':
    print("Memulai server Flask...")
    print("Buka http://127.0.0.1:5000 di browser Anda.")
    app.run(debug=True)

# ======================================================================
# File: templates/index.html
# Letakkan kode di bawah ini di dalam file 'templates/index.html'
# ======================================================================
"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Webcam - Pengukur Objek Real-time</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gray-900 text-white flex flex-col items-center justify-center min-h-screen p-4">

    <div class="w-full max-w-4xl mx-auto bg-gray-800 rounded-2xl shadow-2xl p-6 md:p-8">
        <header class="text-center mb-6">
            <h1 class="text-3xl md:text-4xl font-bold text-cyan-400">📏 Pengukur Objek via Webcam</h1>
            <p class="text-gray-400 mt-2">Streaming video langsung dari server Python (Flask + OpenCV).</p>
        </header>

        <!-- Area Tampilan Video -->
        <div class="relative w-full aspect-video bg-black rounded-xl overflow-hidden shadow-lg">
            <!-- Elemen img ini akan menampilkan streaming dari Flask -->
            <img src="{{ url_for('video_feed') }}" class="w-full h-full object-cover" alt="Video Stream">
        </div>

        <div class="mt-6 text-center text-gray-500 text-sm">
            <p><strong>Catatan:</strong> Pemrosesan video dilakukan di server. Untuk menghentikan, tutup terminal tempat Anda menjalankan 'app.py'.</p>
        </div>
    </div>

</body>
</html>
"""
