from .base_vector_store import BaseVectorStore
import weaviate
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import Filter
from weaviate.classes.data import DataObject
from langchain.schema import Document
from typing import List, Optional, Dict
import json

class WeaviateVectorStore(BaseVectorStore):

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8080,
        grpc_port: int = 50051,
        collection_name: str = 'Document'
    ):
        self.client = weaviate.connect_to_local(host=host, port=port, grpc_port=grpc_port)
        self.collection_name = collection_name

        try:
            self.collection = self.client.collections.get(self.collection_name)
        except weaviate.exceptions.UnexpectedStatusCodeError:
            self.client.collections.create(
                name=self.class_name,
                properties=[
                    Property(name='content', data_type=DataType.TEXT),
                    Property(name='years', data_type=DataType.INT_ARRAY),
                    Property(name='metadata', data_type=DataType.TEXT)
                ]
            )
            self.collection = self.client.collections.get(self.collection_name)

    def close(self):
        if self.client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def add_document(self, doc: Document, embedding: List[float]) -> None:
        probs={
            'content': doc.page_content,
            'years': doc.metadata.get('years', []),
            'metadata': json.dumps(doc.metadata),
        }

        self.collection.data.insert(
            properties=probs,
            vector=embedding
        )
    
    def add_documents(self, docs: List[Document], embeddings: List[List[float]]):
        objects = []
        for doc, embedding in zip(docs, embeddings):
            metadata = doc.metadata
            if not metadata:
                metadata = {}
            obj = DataObject(
                properties={
                    'content': doc.page_content,
                    'years': doc.metadata.get('years', []),
                    'metadata': json.dumps(doc.metadata)
                },
                vector=embedding
            )
            objects.append(obj)
        self.collection.data.insert_many(objects)
    
    def find_all(self) -> List[Document]:
        docs = []
        for item in self.collection.iterator():
            probs = item.properties
            metadata = probs.get('metadata', None)
            if metadata:
                metadata = json.loads(metadata)
            doc = Document(
                page_content=probs.get('content', ''),
                metadata=metadata
            )
            docs.append(doc)
        return docs

    def delete_all(self, limit:int = 1000) -> None:
        offset = 0
        while True:
            response = self.collection.query.fetch_objects(
                offset=offset,
                limit=limit
            )

            ids = [obj.uuid for obj in response.objects]

            self.collection.data.delete_many(
                where=Filter.by_id().contains_any(ids)
            )
    
    def similarity_search(
        self,
        query_vector: List[float],
        k: int = 4,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        response = self.collection.query.near_vector(
            near_vector=query_vector,
            limit=k,
            filters=self.dict_to_filter(filter)
        )
        objects = response.objects
        docs = []
        for obj in objects:
            properties = obj.properties
            metadata = properties.get('metadata', None)
            if metadata:
                metadata = json.loads(metadata)
            docs.append(Document(
                page_content=properties.get('content', ''),
                metadata=metadata
            ))
        return docs
    
    def dict_to_filter(self, dict):
        if not dict:
            return None
        operator = dict.get('operator', None)
        if not operator:
            return None
        if 'operands' in dict:
            operands = dict['operands']
            if not operands or not isinstance(operands, list):
                return None
            filters = [self.dict_to_filter(op) for op in operands]
            if not filters:
                return None
            result = filters[0]
            if not result:
                return None
            for f in filters[1:]:
                if not f:
                    return None
                if operator == 'And':
                    result = result & f
                elif operator == 'Or':
                    result = result | f
                else:
                    return None
            return result
        else:
            path = dict.get('path', None)
            value = dict.get('value', None)
            if not path:
                return None
            prob = Filter.by_property(path)
            if value:
                if operator == 'Equal':
                    return prob.equal(value)
                elif operator == 'NotEqual':
                    return prob.not_equal(value)
                elif operator == 'GreaterThan':
                    return prob.greater_than(value)
                elif operator == 'GreaterThanEqual':
                    return prob.greater_or_equal(value)
                elif operator == 'LessThan':
                    return prob.less_than(value)
                elif operator == 'LessThanEqual':
                    return prob.less_or_equal(value)
                elif operator == 'Like':
                    return prob.like(value)
                elif operator == 'Contains':
                    return prob.like(value)
                else:
                    return None
            else:
                if operator == 'IsNull':
                    return prob.is_none(True)
                elif operator == 'IsNotNull':
                    return prob.is_none(False)
                else:
                    return None
