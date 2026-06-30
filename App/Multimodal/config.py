import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

VISION_MODEL = os.getenv(
    "VISION_MODEL",
    "Salesforce/blip-image-captioning-base",
)

IMAGE_DIR = Path("Data/images")

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tiff",
    ".webp",
}

PRESCRIPTION_KEYWORDS = [
    "prescription",
    "rx",
    "medicine",
    "tablet",
    "capsule",
    "dosage",
    "mg",
    "ml",
    "take",
    "twice daily",
]

LAB_KEYWORDS = [
    "lab",
    "laboratory",
    "hemoglobin",
    "glucose",
    "wbc",
    "rbc",
    "platelet",
    "test result",
    "reference range",
    "specimen",
    "urine",
    "blood test",
]
