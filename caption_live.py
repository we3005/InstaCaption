"""
caption_live.py
----------------
Live webcam captioning for InstaCaption.

Opens your default webcam, periodically runs a frame through the captioning
model, and overlays the resulting caption on the video feed.

Can be run standalone:
    python caption_live.py
    python caption_live.py --camera 1 --interval 1.5

Or imported and used from instacaption.py via run_live_mode().

Controls:
    q  - quit
"""

import argparse
import time

import cv2
from PIL import Image

from captioner import Captioner


def run_live_mode(captioner: Captioner, camera: int = 0, interval: float = 2.0):
    """
    Open the webcam and overlay a live-updating caption on the video feed.
    Reuses an already-loaded Captioner so the model isn't reloaded each time.
    """
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        print(f"Could not open camera index {camera}.")
        return

    print("InstaCaption live mode running. Press 'q' in the video window to quit.")

    current_caption = "..."
    last_caption_time = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read from camera.")
                break

            now = time.time()
            if now - last_caption_time >= interval:
                # BGR (OpenCV) -> RGB (PIL) for the model
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                current_caption = captioner.caption(pil_image)
                last_caption_time = now

            display_frame = draw_caption(frame, current_caption)
            cv2.imshow("InstaCaption - Live", display_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


def draw_caption(frame, text: str):
    """Draw a readable caption bar across the bottom of the frame."""
    h, w = frame.shape[:2]
    bar_height = 60

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - bar_height), (w, h), (0, 0, 0), thickness=-1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

    cv2.putText(
        frame,
        text,
        (10, h - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return frame


def main():
    parser = argparse.ArgumentParser(description="InstaCaption - live webcam captioning")
    parser.add_argument("--camera", type=int, default=0, help="Webcam device index (default: 0)")
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Seconds between captioning updates (default: 2.0). Lower = more responsive but slower/choppier.",
    )
    args = parser.parse_args()

    captioner = Captioner()
    run_live_mode(captioner, camera=args.camera, interval=args.interval)


if __name__ == "__main__":
    main()
