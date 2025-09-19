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
        k: int,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._embedder = embedder
        self._vector_store = vector_store
        self._k = k
    
    def invoke(self, input, config = None, **kwargs) -> List[Document]:
        return self._get_relevant_documents(input)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        query_vector = self._embedder.embed(query)
        years = re.findall(r'\b20\d{2}\b', query)
        if years:
            years = [int(year) for year in years]
        else:
            years = [2025]
        docs = self._vector_store.similarity_search(
            query_vector=query_vector,
            k=self._k,
            filter={
                'operator': 'Contains',
                'path': 'years',
                'value': years
            }
        )

        return docs