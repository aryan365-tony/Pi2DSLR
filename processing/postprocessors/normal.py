from PIL import Image, ImageEnhance, ImageFilter
from .base import BasePostProcessor


class NormalPostProcessor(BasePostProcessor):

    def process(self, filepath, frames=None):
        img = Image.open(filepath).convert("RGB")

        # Slight contrast improvement
        img = ImageEnhance.Contrast(img).enhance(1.1)

        # Slight color boost (avoid oversaturation)
        img = ImageEnhance.Color(img).enhance(1.08)

        # Tiny brightness lift
        img = ImageEnhance.Brightness(img).enhance(1.03)

        # Gentle sharpening
        img = img.filter(
            ImageFilter.UnsharpMask(radius=1.5, percent=110, threshold=3)
        )

        img.save(filepath, quality=95, optimize=True)
