import cv2
import numpy as np
from .base import BasePostProcessor


class VideoPostProcessor(BasePostProcessor):
    """
    Simple electronic video stabilization.
    Produces a stabilized copy of the recorded video.
    """

    def process(self, filepath, frames=None):
        cap = cv2.VideoCapture(filepath)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        out_path = filepath.replace(".mp4", ".mp4")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(out_path, fourcc, fps,
                              (width, height))

        prev_gray = None
        transforms = []
        frames_list = []

        # ---------- Motion estimation ----------
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_gray is None:
                prev_gray = gray
                frames_list.append(frame)
                transforms.append((0, 0))
                continue

            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None,
                0.5, 3, 15, 3, 5, 1.2, 0
            )

            dx = np.mean(flow[..., 0])
            dy = np.mean(flow[..., 1])

            transforms.append((dx, dy))
            frames_list.append(frame)
            prev_gray = gray

        cap.release()

        # ---------- Smooth motion ----------
        smoothed = []
        avg_dx, avg_dy = 0, 0

        for dx, dy in transforms:
            avg_dx = 0.9 * avg_dx + 0.1 * dx
            avg_dy = 0.9 * avg_dy + 0.1 * dy
            smoothed.append((avg_dx, avg_dy))

        # ---------- Apply stabilization ----------
        for frame, (dx, dy) in zip(frames_list, smoothed):
            m = np.float32([[1, 0, -dx],
                            [0, 1, -dy]])

            stabilized = cv2.warpAffine(
                frame, m, (width, height)
            )

            out.write(stabilized)

        out.release()

        print("Stabilized video saved:", out_path)
