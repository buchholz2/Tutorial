# The Binding of Isaac Pedestal Detector

This repository provides a simple Python script to capture the game screen and
search for an item pedestal in *The Binding of Isaac*. It uses
[PyAutoGUI](https://pyautogui.readthedocs.io/) for screen capture and
[OpenCV](https://opencv.org/) for template matching.

## Requirements

- Python 3.8+
- `pyautogui`
- `opencv-python`
- `mss`
- `Pillow`

Install the dependencies with:

```bash
pip install opencv-python pyautogui mss pillow
```

## Usage

1. Capture a screenshot of the item pedestal you want to detect and save it as an
   image file (e.g. `pedestal.png`).
2. Run the detector and provide the template path:

```bash
python pedestal_detector.py pedestal.png
```

Optional arguments:

- `--region X Y W H` — screen region to capture (defaults to full screen).
- `--delay SECONDS` — seconds to wait before the screenshot is taken (defaults
  to `2`).

During the delay you can switch focus to the game window. The script will report
whether it found the pedestal in the captured image and the coordinates of the
match.
