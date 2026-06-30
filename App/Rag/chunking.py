from langchain.text_splitter import RecursiveCharacterTextSplitter
class TextChunker:

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=200
        )

    def split(self, text: str):
        """Split a single string into text chunks."""
        return self.splitter.split_text(text)