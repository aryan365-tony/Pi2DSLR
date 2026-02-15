import sys
from PyQt5.QtWidgets import QApplication
from camera_app import CameraApp


def main():
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
