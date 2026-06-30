from pathlib import Path
import uuid                    #It generates unique ids

from App.Rag.document_loader import UnifiedLoader
from App.Rag.chunking import TextChunker
from App.Rag.embedding_service import EmbeddingService
from App.Rag.vector_store import VectorStore

# Root data folder
DATA_DIR = Path("Data/uploads")


def ingest():

    loader = UnifiedLoader()
    chunker = TextChunker()
    embedder = EmbeddingService()
    store = VectorStore()

    all_chunks = []
    all_metadata = []

    supported_extensions = [
        ".pdf",
        ".docx",
        ".txt"
    ]

    print("\nScanning documents...\n")

    for file in DATA_DIR.rglob("*"):    

        if (
            file.is_file()
            and file.suffix.lower()
            in supported_extensions
        ):

            try:

                print(
                    f"Processing: {file}"
                )

                text = loader.load_document(
                    file
                )

                if not text.strip():

                    print(
                        f"Skipped Empty File: {file.name}"
                    )

                    continue

                chunks = chunker.split(text)

                for chunk in chunks:

                    all_chunks.append(chunk)

                    all_metadata.append(
                        {
                            "source": file.name,
                            "folder": file.parent.name,
                            "path": str(file)
                        }
                    )

            except Exception as e:

                print(
                    f"Error processing {file}: {e}"
                )

    if len(all_chunks) == 0:

        print(
            "No valid document chunks found."
        )

    else:

        print(
            f"\nTotal Chunks Created: {len(all_chunks)}"
        )

        embeddings = embedder.embed_documents(
            all_chunks
        )

        ids = [
            str(uuid.uuid4())
            for _ in range(
                len(all_chunks)
            )
        ]

        store.add(
            ids=ids,
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=all_metadata
        )

        print(
            f"\nSuccessfully stored "
            f"{len(all_chunks)} chunks "
            f"in Vector Database"
        )

    from App.Multimodal.ingest import ingest_images

    ingest_images()


if __name__ == "__main__":
    ingest()