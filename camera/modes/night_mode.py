from .base_mode import BaseMode


class NightMode(BaseMode):
    name = "Night"

    def capture(self, app, filename):
        frames = list(app.camera.frame_buffer.buffer)[-6:]

        if not frames:
            app.camera.capture(filename, app.capture_done)
            return

        app.capture_done(
            None,
            mode="night",
            frames=frames
        )
