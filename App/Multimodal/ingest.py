from .config import ALLOWED_IMAGE_EXTENSIONS, IMAGE_DIR
from .indexer import ImageIndexer


def ingest_images():
    print("\nScanning images...\n")

    indexer = ImageIndexer()

    for file in IMAGE_DIR.rglob("*"):
        if (
            file.is_file()
            and file.suffix.lower() in ALLOWED_IMAGE_EXTENSIONS
        ):
            try:
                print(f"Processing image: {file}")
                indexer.index_image(file)
            except Exception as e:
                print(f"Error processing image {file}: {e}")


if __name__ == "__main__":
    ingest_images()
