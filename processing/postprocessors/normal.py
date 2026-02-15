from PIL import Image, ImageEnhance, ImageFilter
from .base import BasePostProcessor


class NormalPostProcessor(BasePostProcessor):

    def process(self, filepath, frames=None):
        img = Image.open(filepath)

        img = ImageEnhance.Contrast(img).enhance(1.15)
        img = ImageEnhance.Color(img).enhance(1.1)
        img = ImageEnhance.Brightness(img).enhance(1.05)

        img = img.filter(ImageFilter.SHARPEN)
        img.save(filepath, quality=95)
