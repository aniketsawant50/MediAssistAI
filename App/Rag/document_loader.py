from pathlib import Path
from docx import Document
from langchain_community.document_loaders import PyPDFLoader


class UnifiedLoader:

    def load_pdf(self, file_path):
        docs = PyPDFLoader(str(file_path)).load()

        return "\n".join(
            [doc.page_content for doc in docs]
        )

    def load_docx(self, file_path):
        doc = Document(file_path)

        return "\n".join(
            [paragraph.text for paragraph in doc.paragraphs]
        )

    def load_txt(self, file_path):
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()

    def load_document(self, file_path):

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return self.load_pdf(file_path)

        elif extension == ".docx":
            return self.load_docx(file_path)

        elif extension == ".txt":
            return self.load_txt(file_path)

        else:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )