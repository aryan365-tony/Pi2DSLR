from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

from .frame_buffer import FrameBuffer


class CameraController:
    def __init__(self):
        self.picam2 = Picamera2()

        self.capturing = False
        self.recording = False

        # ---------- Frame buffer (ZSL) ----------
        self.frame_buffer = FrameBuffer(size=10)

        # ---------- Preview configuration ----------
        preview_config = self.picam2.create_preview_configuration(
            main={"size": (1280, 720)},
            controls={"FrameRate": 60},
            buffer_count=6
        )

        # ---------- Photo capture ----------
        self.capture_config = self.picam2.create_still_configuration(
            main={"size": self.picam2.sensor_resolution}
        )

        # ---------- Video configuration ----------
        self.video_config = self.picam2.create_video_configuration(
            main={"size": (1920, 1080)},
            controls={
                "FrameRate": 60,
                "FrameDurationLimits": (16666, 16666)
            }
        )

        self.picam2.configure(preview_config)

        # ---------- Default camera tuning ----------
        self.picam2.set_controls({
            # Continuous autofocus
            "AfMode": 2,
            "AfSpeed": 1,

            # Reduce motion blur
            "AeExposureMode": 1,
            "AeMeteringMode": 0,

            # Keep preview smooth
            "FrameDurationLimits": (16666, 16666),
        })

        # Frame arrival callback
        self.picam2.post_callback = self._frame_arrived

        self.fps_callback = None
        self.encoder = None

    # =========================================================
    # Frame arrival handling
    # =========================================================
    def _frame_arrived(self, request):
        frame = request.make_array("main")
        self.frame_buffer.add_frame(frame)

        if self.fps_callback:
            self.fps_callback(request)

    # =========================================================
    # Camera lifecycle
    # =========================================================
    def start(self):
        self.picam2.start()

    def stop(self):
        self.picam2.stop()

    # =========================================================
    # Photo capture
    # =========================================================
    def capture(self, filename, callback):
        if self.capturing:
            return

        self.capturing = True

        def done(job):
            self.capturing = False
            callback(job)

        self.picam2.switch_mode_and_capture_file(
            self.capture_config,
            filename,
            signal_function=done
        )

    # Zero shutter lag capture
    def capture_from_buffer(self, filename):
        frame = self.frame_buffer.get_latest()
        if frame is None:
            return False

        from PIL import Image

        img = Image.fromarray(frame)

        # Remove alpha channel if present
        if img.mode in ("RGBA", "BGRA"):
            img = img.convert("RGB")

        img.save(filename, quality=95)
        return True

    # =========================================================
    # Video recording
    # =========================================================
    def start_recording(self, filename):
        if self.recording:
            return

        self.picam2.stop()

        # Switch to video configuration
        self.picam2.configure(self.video_config)

        # iPhone-like video tuning
        self.picam2.set_controls({
            "Contrast": 1.15,
            "Saturation": 1.2,
            "Brightness": 0.05,
            "Sharpness": 1.1,

            # Continuous autofocus
            "AfMode": 2,
            "AfSpeed": 1,

            # Motion blur reduction
            "AeExposureMode": 1,
            "FrameDurationLimits": (16666, 16666),
        })

        self.picam2.start()

        # High quality bitrate for 1080p60
        self.encoder = H264Encoder(bitrate=20000000)

        output = FfmpegOutput(filename)

        self.picam2.start_recording(self.encoder, output)
        self.recording = True

    def stop_recording(self):
        if not self.recording:
            return

        self.picam2.stop_recording()

        # Restore preview configuration
        self.picam2.stop()

        preview_config = self.picam2.create_preview_configuration(
            main={"size": (1280, 720)},
            controls={"FrameRate": 60},
            buffer_count=6
        )

        self.picam2.configure(preview_config)
        self.picam2.start()

        self.recording = False
