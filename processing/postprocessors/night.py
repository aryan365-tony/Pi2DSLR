import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from .base import BasePostProcessor
from processing.image_utils import align_frames_fast


class NightPostProcessor(BasePostProcessor):

    def process(self, filepath, frames=None):
        if not frames:
            return

        frames = frames[-6:]

        aligned = align_frames_fast(frames)
        arrays = [f.astype(np.float32) for f in aligned]

        avg = np.mean(arrays, axis=0)
        avg = np.clip(avg, 0, 255).astype(np.uint8)

        img = Image.fromarray(avg)

        img = ImageEnhance.Brightness(img).enhance(1.2)
        img = ImageEnhance.Contrast(img).enhance(1.1)
        img = img.filter(ImageFilter.SHARPEN)

        img.save(filepath, quality=95)
