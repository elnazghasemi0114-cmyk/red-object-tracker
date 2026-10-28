# Red Object Tracker

A real-time computer vision project built with Python, OpenCV, and NumPy.

## Features

- Real-time red object detection using HSV color segmentation
- Object tracking with unique IDs
- Simultaneous tracking of multiple objects
- Object movement trails
- Approximate speed estimation in pixels per second
- Temporary object disappearance handling

## Requirements

- Python
- OpenCV
- NumPy
- A webcam

## Installation

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd red-object-tracker
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

## Usage

Run the tracker:

```bash
python red_object_tracker.py
```

Press `q` to close the camera window.

## How It Works

The program converts each camera frame from BGR to HSV color space and creates masks for red color ranges. It detects contours, calculates object centers, and matches detected objects with previous positions to track them over time.

Movement speed is estimated in pixels per second (`px/s`). It is an approximate image-space measurement, not real-world physical speed.

## Limitations

- Tracking may become less reliable when objects overlap or cross paths.
- Detection depends on lighting and the object's color.
- Speed is measured in image pixels rather than meters per second.

## Future Improvements

- Improve object matching when objects cross paths
- Add support for more colors
- Save tracking results for later analysis

## Author

Created as a computer vision learning project.
