import cv2
import numpy as np
from mss import mss
import argparse
import time


def capture_region(region=None):
    """Grab a screenshot of the given region.

    Parameters
    ----------
    region : tuple[int, int, int, int] or None
        Coordinates ``(x, y, width, height)`` of the region to capture. If
        ``None``, the primary monitor is captured.
    """
    with mss() as sct:
        monitor = (
            sct.monitors[0]
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


def match_template_multi_scale(
    img,
    template,
    threshold=0.8,
    scale_min=0.8,
    scale_max=1.2,
    scale_step=0.1,
    scale_target="template",
):
    """Perform template matching over a range of scales.

    Parameters
    ----------
    img : numpy.ndarray
        Screenshot image.
    template : numpy.ndarray
        Template image to search for.
    threshold : float, optional
        Minimum matching score required to return a match.
    scale_min, scale_max, scale_step : float, optional
        Range of scales to try. ``scale_max`` is inclusive.
    scale_target : {"template", "screenshot"}
        Whether to resize the template (default) or the screenshot.

    Returns
    -------
    tuple or None
        ``(top_left, bottom_right, score, scale)`` if a match above the
        threshold is found, otherwise ``None``.
    """

    best = None
    best_score = -1.0

    scales = np.arange(scale_min, scale_max + scale_step / 2, scale_step)
    for scale in scales:
        if scale_target == "template":
            scaled_template = cv2.resize(
                template,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR,
            )
            if (
                scaled_template.shape[0] > img.shape[0]
                or scaled_template.shape[1] > img.shape[1]
            ):
                continue
            result = cv2.matchTemplate(img, scaled_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > best_score:
                h, w = scaled_template.shape[:2]
                best = (max_loc, (max_loc[0] + w, max_loc[1] + h), max_val, scale)
                best_score = max_val
        else:  # scale the screenshot
            scaled_img = cv2.resize(
                img,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR,
            )
            result = cv2.matchTemplate(scaled_img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > best_score:
                h, w = template.shape[:2]
                top_left = (int(max_loc[0] / scale), int(max_loc[1] / scale))
                bottom_right = (
                    int((max_loc[0] + w) / scale),
                    int((max_loc[1] + h) / scale),
                )
                best = (top_left, bottom_right, max_val, scale)
                best_score = max_val

    if best is not None and best[2] >= threshold:
        return best
    return None


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
        "--scale-min",
        type=float,
        help="Minimum scale factor for multi-scale search",
    )
    parser.add_argument(
        "--scale-max",
        type=float,
        help="Maximum scale factor for multi-scale search",
    )
    parser.add_argument(
        "--scale-step",
        type=float,
        help="Step size between scales for multi-scale search",
    )
    parser.add_argument(
        "--scale-target",
        choices=["template", "screenshot"],
        default="template",
        help="Resize this image when performing multi-scale search",
    )
    args = parser.parse_args()

    time.sleep(args.delay)
    img = capture_region(args.region)
    template = cv2.imread(args.template)
    if template is None:
        print("Could not load template image:", args.template)
        return

    use_multi_scale = (
        args.scale_min is not None
        or args.scale_max is not None
        or args.scale_step is not None
        or args.scale_target != "template"
    )

    if use_multi_scale:
        match = match_template_multi_scale(
            img,
            template,
            scale_min=args.scale_min or 0.8,
            scale_max=args.scale_max or 1.2,
            scale_step=args.scale_step or 0.1,
            scale_target=args.scale_target,
        )
    else:
        match = match_template(img, template)

    if match:
        if len(match) == 4:
            top_left, bottom_right, score, scale = match
            print(
                f"Pedestal found with score {score:.2f} at {top_left} -> {bottom_right} (scale {scale:.2f})"
            )
        else:
            top_left, bottom_right, score = match
            print(
                f"Pedestal found with score {score:.2f} at {top_left} -> {bottom_right}"
            )
    else:
        print("Pedestal not found.")


if __name__ == "__main__":
    main()
