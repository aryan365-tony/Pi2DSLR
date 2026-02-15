from collections import deque
import threading


class FrameBuffer:
    def __init__(self, size=10):
        self.buffer = deque(maxlen=size)
        self.lock = threading.Lock()

    def add_frame(self, frame):
        with self.lock:
            self.buffer.append(frame.copy())

    def get_latest(self):
        with self.lock:
            if self.buffer:
                return self.buffer[-1].copy()
            return None
