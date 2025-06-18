# The Binding of Isaac Utilities

This repository contains resources and a Python tool to detect item pedestals in *The Binding of Isaac*.
It also ships with JSON files describing game items and trinkets.

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

1. Capture a screenshot of the item pedestal you want to detect and save it as an image file (e.g. `images/pedestal.png`).
2. Run the detector and provide the template path:

```bash
python src/pedestal_detector.py images/pedestal.png
```

Optional arguments:

- `--region X Y W H` — screen region to capture (defaults to full screen).
- `--delay SECONDS` — seconds to wait before the screenshot is taken (defaults to `2`).

During the delay you can switch focus to the game window. The script will report whether it found the pedestal in the captured image and the coordinates of the match.

The `data/` directory holds JSON files with item and trinket descriptions that can be consumed by other tools.
