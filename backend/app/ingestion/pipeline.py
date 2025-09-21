from .loaders.base_loader import BaseLoader
from .splitters.base_splitter import BaseSplitter
from .embedders.base_embedder import BaseEmbedder
from .vector_stores.base_vector_store import BaseVectorStore
from typing import List, Dict, Any
from .loaders.link_loader import LinkLoader
from .loaders.pdf_loader import PDFLoader
from .loaders.web_loader import WebLoader
from .embedders.hugging_face_embedder import HuggingFaceEmbedder
from .vector_stores.weaviate_vector_store import WeaviateVectorStore
from .splitters.heading_splitter import HeadingSplitter
from .splitters.character_size_splitter import CharacterSizeSplitter
from ..config import settings

class IngestionPipeline:
    def __init__(self):
        self.link_loader = LinkLoader()
        self.web_loader = WebLoader(config=settings.WEB_LOADER_CONFIG)
        self.pdf_loader = PDFLoader()
        self.heading_splitter = HeadingSplitter()
        self.character_size_splitter = CharacterSizeSplitter(
            chunk_size=settings.CHARACTER_SPLITTER_CONFIG['chunk_size'],
            chunk_overlap=settings.CHARACTER_SPLITTER_CONFIG['chunk_overlap']
        )
        self.embedder = HuggingFaceEmbedder(settings.HUGGING_FACE_EMBEDDER_CONFIG['model_name'])
        self.vector_store = WeaviateVectorStore(
            host=settings.WEAVIATE_CONFIG['host'],
            port=settings.WEAVIATE_CONFIG['port'],
            grpc_port=settings.WEAVIATE_CONFIG['grpc_port'],
            collection_name=settings.WEAVIATE_CONFIG['collection_name']
        )
    
    def close(self):
        self.vector_store.close()
    
    def run(
        self,
        links_paths: List[str],
        pdf_paths: List[str],
    ):
        docs = []
        for link_path in links_paths:
            link_docs = self.link_loader.load(link_path)
            for link_doc in link_docs:
                web_docs = self.web_loader.load(
                    path=link_doc.page_content,
                    metadata=link_doc.metadata
                )
                web_docs = self.heading_splitter.split(web_docs)
                web_docs = self.character_size_splitter.split(web_docs)
                docs.extend(web_docs)
        for pdf_path in pdf_paths:
            pdf_docs = self.pdf_loader.load(pdf_path)
            pdf_docs = self.heading_splitter.split(pdf_docs)
            pdf_docs = self.character_size_splitter.split(pdf_docs)
            docs.extend(pdf_docs)
        
        embeddings = []
        contents = [doc.page_content for doc in docs]
        headings = [' - '.join(doc.metadata.get('headings', [])) for doc in docs]
        BATCH_SIZE = 32
        content_vectors = self.embedder.embed_batch(
            [content for content in contents if content], 
            batch_size=BATCH_SIZE
        )
        heading_vectors = self.embedder.embed_batch(
            [heading for heading in headings if heading], 
            batch_size=BATCH_SIZE
        )
        content_vector_id = 0
        heading_vector_id = 0
        for i in range(len(docs)):
            embedding = {}
            if contents[i]:
                embedding['content_vector'] = content_vectors[content_vector_id]
                content_vector_id += 1
            if headings[i]:
                embedding['heading_vector'] = heading_vectors[heading_vector_id]
                heading_vector_id += 1
            embeddings.append(embedding)

        self.vector_store.add_documents(
            docs=docs,
            embeddings=embeddings
        )
