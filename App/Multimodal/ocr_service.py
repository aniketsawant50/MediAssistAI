from pathlib import Path


class OCRService:

    def __init__(self):
        self._reader = None

    def _get_reader(self):
        if self._reader is None:
            import easyocr

            self._reader = easyocr.Reader(["en"], gpu=False)
        return self._reader

    def extract_text(self, image_path: Path) -> str:
        reader = self._get_reader()
        lines = reader.readtext(str(image_path), detail=0)
        return "\n".join(line.strip() for line in lines if line.strip())
