from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from langchain.schema import Document

class BaseVectorStore(ABC):

    @abstractmethod
    def add_document(self, doc: Document, embedding: List[float]) -> None:
        pass

    def add_documents(self, docs: List[Document], embeddings: List[List[float]]) -> None:
        if len(docs) != len(embeddings):
            raise ValueError('docs and embeddings must have the same size.')
        for doc, embedding in zip(docs, embeddings):
            self.add_document(doc, embedding)
    
    @abstractmethod
    def similarity_search(self, query_vector: List[float], k: int, filter: Optional[Dict]) -> List[Document]:
        pass
