from typing import List, Union
from abc import ABC, abstractmethod
from langchain.schema import Document

class BaseEmbedder(ABC):
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        return [self.embed(text) for text in texts]

    def embed_document(self, doc: Document) -> List[float]:
        return self.embed(doc.page_content)

    def embed_documents(self, docs: List[Document], batch_size: int = 32) -> List[List[float]]:
        return self.embed_batch([doc.page_content for doc in docs], batch_size=batch_size)
