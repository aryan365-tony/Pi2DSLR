from .normal_mode import NormalMode
from .night_mode import NightMode
from .video_mode import VideoMode

AVAILABLE_MODES = [
    NormalMode(),
    NightMode(),
    VideoMode(),
]
