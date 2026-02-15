from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtCore import Qt


def make_thumbnail():
    label = QLabel()
    label.setFixedSize(120, 90)
    label.setStyleSheet("background:black;")
    label.setAlignment(Qt.AlignCenter)
    return label


def make_capture_button(callback):
    btn = QPushButton("CAPTURE")
    btn.setFixedSize(140, 60)
    btn.clicked.connect(callback)
    return btn
