from .base_vector_store import BaseVectorStore
import weaviate
from langchain.schema import Document
from typing import List
import json

class WeaviateVectorStore(BaseVectorStore):

    def __init__(self, endpoint: str, class_name: str):
        self.client = weaviate.Client(endpoint)
        self.class_name = class_name

        if not self.client.schema.exists(self.class_name):
            schema = {
                'classes': [
                    {
                        'class': self.class_name,
                        'properties': [
                            { 'name': 'text', 'dataType': 'text' },
                            { 'name': 'years', 'dataType': 'text' },
                            { 'name': 'metadata', 'dataType': 'text' }
                        ],
                        'vectorizer': 'none'
                    }
                ],
            }
            self.client.schema.create(schema)
        
    def add_document(self, doc: Document, embedding: List[float]):
        years = None
        if doc.metadata.get('years'):
            years = ' - '.join(doc.metadata['years'])
        self.client.data_object.create(
            data_object={
                'text': doc.page_content,
                'years': years,
                'metadata': json.dumps(doc.metadata),
            },
            class_name=self.class_name,
            vector=embedding
        )
    
    def add_documents(self, docs: List[Document], embeddings: List[List[float]]):
        with self.client.batch as batch:
            batch.batch_size = 50
            for doc, embedding in zip(docs, embeddings):
                years = None
                if doc.metadata.get('years'):
                    years = ' - '.join(doc.metadata['years'])
                batch.add_data_object(
                    data_object={
                        'text': doc.page_content,
                        'years': years,
                        'metadata': json.dumps(doc.metadata)
                    },
                    class_name=self.class_name,
                    vector=embedding
                )