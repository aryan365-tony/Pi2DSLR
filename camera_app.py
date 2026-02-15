import os
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

from picamera2.previews.qt import QGlPicamera2

from camera.controller import CameraController
from camera.modes import AVAILABLE_MODES
from processing.processing_worker import ProcessingWorker
from ui.widgets import make_thumbnail, make_capture_button


SAVE_DIR = os.path.expanduser("~/Videos")
os.makedirs(SAVE_DIR, exist_ok=True)


class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pi Camera")
        self.showFullScreen()

        self.camera = CameraController()
        self.camera.fps_callback = self.frame_arrived

        self.modes = AVAILABLE_MODES
        self.mode_index = 0
        self.current_mode = self.modes[0]

        # Preview
        self.preview = QGlPicamera2(self.camera.picam2)
        self.preview.setFixedSize(1280, 720)

        # FPS label
        self.fps_label = QLabel("FPS: 0", self.preview)
        self.fps_label.move(10, 10)
        self.fps_label.setStyleSheet(
            "color:white;background:rgba(0,0,0,120);padding:4px;"
        )

        # Mode label
        self.mode_label = QLabel(self.current_mode.name, self.preview)
        self.mode_label.move(10, 50)
        self.mode_label.setStyleSheet(
            "color:white;background:rgba(0,0,0,120);padding:4px;"
        )

        # ---------- Recording UI ----------
        self.recording_label = QLabel("● REC 00:00", self.preview)
        self.recording_label.move(10, 90)
        self.recording_label.setStyleSheet(
            "color:red;background:rgba(0,0,0,120);padding:6px;"
        )
        self.recording_label.hide()

        self.record_seconds = 0

        self.record_timer = QTimer()
        self.record_timer.timeout.connect(self.update_recording_time)

        # ---------- FPS counter ----------
        self.frame_count = 0
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_fps)
        self.fps_timer.start(1000)

        # ---------- Controls ----------
        self.thumbnail = make_thumbnail()
        self.capture_button = make_capture_button(self.capture_image)

        self.mode_button = QPushButton("MODE")
        self.mode_button.clicked.connect(self.cycle_mode)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.thumbnail)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.capture_button)
        bottom_layout.addWidget(self.mode_button)
        bottom_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.preview, alignment=Qt.AlignCenter)
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Flash overlay
        self.flash_overlay = QLabel(self)
        self.flash_overlay.setStyleSheet("background:white;")
        self.flash_overlay.hide()

        self.camera.start()

    # ---------- Mode cycling ----------
    def cycle_mode(self):
        self.mode_index = (self.mode_index + 1) % len(self.modes)
        self.current_mode = self.modes[self.mode_index]
        self.mode_label.setText(self.current_mode.name)

    # ---------- FPS ----------
    def frame_arrived(self, request):
        self.frame_count += 1

    def update_fps(self):
        self.fps_label.setText(f"FPS: {self.frame_count}")
        self.frame_count = 0

    # ---------- Recording UI ----------
    def start_recording_ui(self):
        self.record_seconds = 0
        self.recording_label.setText("● REC 00:00")
        self.recording_label.show()
        self.record_timer.start(1000)

    def stop_recording_ui(self):
        self.record_timer.stop()
        self.recording_label.hide()

    def update_recording_time(self):
        self.record_seconds += 1
        minutes = self.record_seconds // 60
        seconds = self.record_seconds % 60
        self.recording_label.setText(
            f"● REC {minutes:02d}:{seconds:02d}"
        )

    # ---------- Capture ----------
    def capture_image(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.current_mode.name == "Video":
            filename = os.path.join(
                SAVE_DIR, f"VID_{timestamp}.mp4"
            )

            if self.camera.recording:
                self.current_mode.capture(self, filename)
                self.stop_recording_ui()
                self.worker = ProcessingWorker(filename,mode="video")
                self.worker.start()
                self.capture_button.setText("CAPTURE")
            else:
                self.current_mode.capture(self, filename)
                self.start_recording_ui()
                self.capture_button.setText("STOP")

            return

        # Photo modes
        self.capture_button.setEnabled(False)

        self.filename = os.path.join(
            SAVE_DIR, f"IMG_{timestamp}.jpg"
        )

        self.flash_animation()
        self.current_mode.capture(self, self.filename)

    # ---------- Capture finished ----------
    def capture_done(self, job, mode="normal", frames=None):
        self.worker = ProcessingWorker(
            self.filename,
            mode=mode,
            frames=frames
        )
        self.worker.finished.connect(self.processing_done)
        self.worker.start()

    def processing_done(self, filepath):
        self.update_thumbnail(filepath)
        self.capture_button.setEnabled(True)

    # ---------- Flash ----------
    def flash_animation(self):
        self.flash_overlay.setGeometry(0, 0, self.width(), self.height())
        self.flash_overlay.show()
        QTimer.singleShot(120, self.flash_overlay.hide)

    # ---------- Thumbnail ----------
    def update_thumbnail(self, filepath):
        pixmap = QPixmap(filepath)
        pixmap = pixmap.scaled(
            self.thumbnail.width(),
            self.thumbnail.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.thumbnail.setPixmap(pixmap)

    # ---------- Exit ----------
    def closeEvent(self, event):
        self.camera.stop()
        event.accept()
