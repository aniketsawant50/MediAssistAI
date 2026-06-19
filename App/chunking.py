from langchain.text_splitter import RecursiveCharacterTextSplitter
class TextChunker:

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100
        )

    def split(self, text: str):
        """Split a single string into text chunks."""
        return self.splitter.split_text(text)