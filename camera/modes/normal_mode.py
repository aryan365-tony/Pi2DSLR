from .base_mode import BaseMode


class NormalMode(BaseMode):
    name = "Normal"

    def capture(self, app, filename):
        saved = app.camera.capture_from_buffer(filename)

        if saved:
            app.capture_done(None, mode="normal")
        else:
            app.camera.capture(filename, app.capture_done)
