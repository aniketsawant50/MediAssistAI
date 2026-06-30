from pathlib import Path

from .config import VISION_MODEL


class VisionService:
    """BLIP vision captioning without the deprecated image-to-text pipeline."""

    def __init__(self):
        self._processor = None
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return

        from transformers import BlipForConditionalGeneration, BlipProcessor

        self._processor = BlipProcessor.from_pretrained(VISION_MODEL)
        self._model = BlipForConditionalGeneration.from_pretrained(VISION_MODEL)

    def extract_caption(self, image_path: Path) -> str:
        from PIL import Image

        self._load_model()
        image = Image.open(image_path).convert("RGB")
        inputs = self._processor(image, return_tensors="pt")
        output = self._model.generate(**inputs, max_length=50)
        return self._processor.decode(output[0], skip_special_tokens=True).strip()
