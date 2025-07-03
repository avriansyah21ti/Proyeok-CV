# Webcam Real-time Object Measurer

## Description

This project is a web application that uses your webcam to detect objects in real-time and measure their dimensions (e.g., diameter, circumference, width, height) in centimeters. It leverages Flask for the web framework and OpenCV for computer vision tasks.

## Features

-   Real-time video streaming from your webcam.
-   Detects circular and rectangular objects.
-   Measures the diameter and circumference of circular objects.
-   Measures the width and height of rectangular objects.
-   Displays measurements directly on the video stream.
-   Simple web interface to view the stream.

## Requirements

-   Python 3.x
-   Flask
-   OpenCV-Python (`cv2`)
-   NumPy

## Installation

1.  **Clone the repository (if applicable) or download the project files.**
2.  **Install the required Python packages:**
    ```bash
    pip install Flask opencv-python numpy
    ```

## Usage

1.  **Navigate to the project directory in your terminal.**
2.  **Run the Flask application:**
    ```bash
    python proyekCv.py
    ```
3.  **Open your web browser and go to:** `http://127.0.0.1:5000`
4.  You should see the webcam feed with object measurements overlaid.

## Note

-   The video processing is done on the server-side (where you run `proyekCv.py`).
-   To stop the application, close the terminal where the `python proyekCv.py` command is running (usually by pressing `Ctrl+C`).
-   The accuracy of the measurements depends on the `PIXELS_PER_CM` calibration value in `proyekCv.py`. You might need to adjust this value based on your camera and setup for more precise measurements. Currently, it's set to `37.0`.
