from langchain.schema import BaseRetriever, Document
from ..ingestion.embedders.base_embedder import BaseEmbedder
from ..ingestion.vector_stores.base_vector_store import BaseVectorStore
from typing import List
import re

class Retriever(BaseRetriever):
    def __init__(
        self, 
        embedder: BaseEmbedder, 
        vector_store: BaseVectorStore,
        k: int
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.k = k
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        query_vector = self.embedder.embed(query)
        years = re.findall(r'\b20\d{2}\b', query)
        if years:
            years = [int(year) for year in years]
        else:
            years = [2025]
        docs = self.vector_store.similarity_search(
            query_vector=query_vector,
            k=self.k,
            filter={
                'operator': 'Contains',
                'path': 'years',
                'value': years
            }
        )

        return docs