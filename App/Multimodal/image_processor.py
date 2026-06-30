import re
from pathlib import Path
from typing import Dict

from .config import LAB_KEYWORDS, PRESCRIPTION_KEYWORDS
from .ocr_service import OCRService
from .vision_service import VisionService


class ImageProcessor:
    """Extract text and visual context from medical images using EasyOCR and BLIP."""

    def __init__(self):
        self.ocr = OCRService()
        self.vision = VisionService()

    @staticmethod
    def detect_document_type(ocr_text: str, caption: str) -> str:
        combined = f"{ocr_text} {caption}".lower()

        if any(keyword in combined for keyword in PRESCRIPTION_KEYWORDS):
            return "prescription"

        if any(keyword in combined for keyword in LAB_KEYWORDS):
            return "lab_report"

        return "medical_image"

    @staticmethod
    def _extract_labeled_values(ocr_text: str) -> Dict[str, str]:
        fields: Dict[str, str] = {}
        patterns = {
            "patient_name": r"(?:patient(?:\s*name)?|name)\s*[:\-]\s*(.+)",
            "doctor_name": r"(?:dr\.?|doctor|physician)\s*[:\-]?\s*(.+)",
            "date": r"(?:date|dated)\s*[:\-]\s*(.+)",
            "age": r"(?:age)\s*[:\-]\s*(.+)",
            "gender": r"(?:sex|gender)\s*[:\-]\s*(.+)",
        }

        for field, pattern in patterns.items():
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                fields[field] = match.group(1).strip()

        return fields

    def build_structured_document(
        self,
        filename: str,
        ocr_text: str,
        caption: str,
        doc_type: str,
    ) -> str:
        fields = self._extract_labeled_values(ocr_text)

        lines = [
            "[Medical Image Document]",
            f"Source File: {filename}",
            f"Document Type: {doc_type.replace('_', ' ').title()}",
            f"Visual Description: {caption}",
        ]

        if fields:
            lines.append("Structured Fields:")
            for key, value in fields.items():
                label = key.replace("_", " ").title()
                lines.append(f"- {label}: {value}")

        if ocr_text.strip():
            lines.append("OCR Extracted Text:")
            lines.append(ocr_text.strip())
        else:
            lines.append("OCR Extracted Text: No readable text detected.")

        return "\n".join(lines)

    def process_image(self, image_path: Path) -> Dict[str, str]:
        ocr_text = self.ocr.extract_text(image_path)
        caption = self.vision.extract_caption(image_path)
        doc_type = self.detect_document_type(ocr_text, caption)
        structured_text = self.build_structured_document(
            image_path.name,
            ocr_text,
            caption,
            doc_type,
        )

        return {
            "filename": image_path.name,
            "doc_type": doc_type,
            "caption": caption,
            "ocr_text": ocr_text,
            "structured_text": structured_text,
        }
