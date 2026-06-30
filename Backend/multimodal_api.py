from pathlib import Path
import shutil

from fastapi import APIRouter, File, UploadFile

from App.Multimodal.config import ALLOWED_IMAGE_EXTENSIONS, IMAGE_DIR
from App.Multimodal.indexer import ImageIndexer

router = APIRouter(tags=["multimodal"])

IMAGE_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            return {
                "error": (
                    "Only image files are allowed "
                    "(JPG, JPEG, PNG, BMP, TIFF, WEBP)."
                )
            }

        file_path = IMAGE_DIR / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        indexer = ImageIndexer()
        result = indexer.index_image(file_path)

        return {
            "message": "Image uploaded and indexed successfully",
            **result,
        }

    except Exception as e:
        return {"error": str(e)}


@router.get("/images")
def list_images():
    try:
        files = [
            file.name
            for file in IMAGE_DIR.glob("*")
            if file.is_file()
            and file.suffix.lower() in ALLOWED_IMAGE_EXTENSIONS
        ]

        return {
            "total_images": len(files),
            "images": files,
        }

    except Exception as e:
        return {"error": str(e)}
