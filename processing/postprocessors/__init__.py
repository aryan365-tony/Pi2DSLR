from .normal import NormalPostProcessor
from .night import NightPostProcessor
from .video import VideoPostProcessor

POSTPROCESSORS = {
    "normal": NormalPostProcessor(),
    "night": NightPostProcessor(),
    "video": VideoPostProcessor(),
}
