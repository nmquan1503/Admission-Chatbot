from .loaders.base_loader import BaseLoader
from .splitters.base_splitter import BaseSplitter
from .embedders.base_embedder import BaseEmbedder
from .vector_stores.base_vector_store import BaseVectorStore
from typing import List, Dict, Any

class IngestionPipeline:
    def __init__(
        self,
        link_loader: BaseLoader,
        web_loader: BaseLoader,
        pdf_loader: BaseLoader,
        heading_splitter: BaseSplitter,
        character_size_splitter: BaseSplitter,
        embedder: BaseEmbedder,
        vector_store: BaseVectorStore,
    ):
        self.link_loader = link_loader
        self.web_loader = web_loader
        self.pdf_loader = pdf_loader
        self.heading_splitter = heading_splitter
        self.character_size_splitter = character_size_splitter
        self.embedder = embedder
        self.vector_store = vector_store
    
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
