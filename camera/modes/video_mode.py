from .base_mode import BaseMode


class VideoMode(BaseMode):
    name = "Video"

    def capture(self, app, filename):
        if app.camera.recording:
            app.camera.stop_recording()
            app.capture_button.setText("CAPTURE")
        else:
            app.camera.start_recording(filename.replace(".jpg", ".h264"))
            app.capture_button.setText("STOP")
