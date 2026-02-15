from PyQt5.QtCore import QThread, pyqtSignal
from processing.postprocessors import POSTPROCESSORS


class ProcessingWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, filepath, mode="normal", frames=None):
        super().__init__()
        self.filepath = filepath
        self.mode = mode
        self.frames = frames

    def run(self):
        processor = POSTPROCESSORS.get(self.mode)

        if processor:
            processor.process(self.filepath, self.frames)

        self.finished.emit(self.filepath)
