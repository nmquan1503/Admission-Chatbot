from .ingestion.pipeline import IngestionPipeline
from .ingestion.loaders.link_loader import LinkLoader
from .ingestion.loaders.web_loader import WebLoader
from .ingestion.loaders.pdf_loader import PDFLoader
from .ingestion.splitters.heading_splitter import HeadingSplitter
from .ingestion.splitters.character_size_splitter import CharacterSizeSplitter
from .ingestion.embedders.hugging_face_embedder import HuggingFaceEmbedder
from .ingestion.vector_stores.weaviate_vector_store import WeaviateVectorStore
from .config import settings

link_loader = LinkLoader()
web_loader = WebLoader(settings.WEB_LOADER_CONFIG)
pdf_loader = PDFLoader()

heading_splitter = HeadingSplitter()
character_size_splitter = CharacterSizeSplitter(
    chunk_size=settings.CHARACTER_SPLITTER_CONFIG['chunk_size'],
    chunk_overlap=settings.CHARACTER_SPLITTER_CONFIG['chunk_overlap']
)

embedder = HuggingFaceEmbedder(model_name=settings.HUGGING_FACE_EMBEDDER_CONFIG['model_name'])

vector_loader = WeaviateVectorStore(
    host=settings.WEAVIATE_CONFIG['host'],
    port=settings.WEAVIATE_CONFIG['port'],
    grpc_port=settings.WEAVIATE_CONFIG['grpc_port'],
    collection_name=settings.WEAVIATE_CONFIG['collection_name']
)

try:
    if settings.INGESTION_CONFIG['run']:
        ingestion_pipeline = IngestionPipeline(
            link_loader=link_loader,
            web_loader=web_loader,
            pdf_loader=pdf_loader,
            heading_splitter=heading_splitter,
            character_size_splitter=character_size_splitter,
            embedder=embedder,
            vector_store=vector_loader
        )

        ingestion_pipeline.run(
            links_paths=settings.INGESTION_CONFIG['link_paths'],
            pdf_paths=settings.INGESTION_CONFIG['pdf_paths']
        )
finally:
    vector_loader.close()