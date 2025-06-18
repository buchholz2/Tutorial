import cv2
import numpy as np
from mss import mss
import argparse
import time

try:
    import pygetwindow as gw
except Exception:  # pragma: no cover - optional dependency may fail
    gw = None


def capture_region(region=None):
    """Grab a screenshot of the given region.

    Parameters
    ----------
    region : tuple[int, int, int, int] or None
        Coordinates ``(x, y, width, height)`` of the region to capture. If
        ``None``, the primary monitor is captured.  ``sct.monitors[0]`` would
        instead grab the entire virtual screen spanning all monitors.
    """
    with mss() as sct:
        monitor = (
            sct.monitors[1]  # index 0 represents all monitors together
            if region is None
            else {"left": region[0], "top": region[1], "width": region[2], "height": region[3]}
        )
        img = np.array(sct.grab(monitor))
        # mss returns BGRA; drop the alpha channel
        return img[:, :, :3]


def match_template(img, template, threshold=0.8):
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        h, w = template.shape[:2]
        return max_loc, (max_loc[0] + w, max_loc[1] + h), max_val
    return None


def get_window_region(title: str):
    """Return ``(x, y, width, height)`` of the window with the given title."""
    if gw is None:
        raise RuntimeError("pygetwindow is required for --window-title")

    windows = gw.getWindowsWithTitle(title)
    if not windows:
        raise RuntimeError(f"Window '{title}' not found")

    win = windows[0]
    return win.left, win.top, win.width, win.height


def main():
    parser = argparse.ArgumentParser(
        description="Detect item pedestal in Binding of Isaac screenshot"
    )
    parser.add_argument("template", help="Path to item pedestal template image")
    parser.add_argument(
        "--region",
        type=int,
        nargs=4,
        metavar=("X", "Y", "W", "H"),
        help="Screen region to capture",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2,
        help="Seconds to wait before capturing the screen",
    )
    parser.add_argument(
        "--window-title",
        default="The Binding of Isaac",
        help="Window title to capture if --region is not provided",
    )
    args = parser.parse_args()

    time.sleep(args.delay)
    region = args.region
    if region is None and args.window_title:
        try:
            region = get_window_region(args.window_title)
        except Exception as exc:
            print(exc)
            return

    img = capture_region(region)
    template = cv2.imread(args.template)
    if template is None:
        print("Could not load template image:", args.template)
        return

    match = match_template(img, template)
    if match:
        top_left, bottom_right, score = match
        print(
            f"Pedestal found with score {score:.2f} at {top_left} -> {bottom_right}"
        )
    else:
        print("Pedestal not found.")


if __name__ == "__main__":
    main()
