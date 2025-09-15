from .base_splitter import BaseSplitter
from typing import List
from langchain.schema import Document

class CharacterSizeSplitter(BaseSplitter):
    def __init__(self, chunk_size: int, chunk_overlap: int):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split(self, docs: List[Document]) -> List[Document]:
        new_docs = []
        for doc in docs:
            content = doc.page_content
            length = len(content)
            if length <= self.chunk_size:
                new_docs.append(doc)
            else:
                for i in range(0, length, self.chunk_size - self.chunk_overlap):
                    text = content[i : i + self.chunk_size]
                    new_docs.append(Document(
                        page_content=text,
                        metadata=doc.metadata.copy()
                    ))

        total_chunks = len(new_docs)
        for i, doc in enumerate(new_docs):
            doc.metadata['chunk_index'] = i
            doc.metadata['total_chunks'] = total_chunks

        return new_docs
