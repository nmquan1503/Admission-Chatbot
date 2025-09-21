from .ingestion.pipeline import IngestionPipeline
from .config import settings

if settings.INGESTION_CONFIG['run']:
    ingestion_pipeline = IngestionPipeline()
    ingestion_pipeline.run(
        links_paths=settings.INGESTION_CONFIG['link_paths'],
        pdf_paths=settings.INGESTION_CONFIG['pdf_paths']
    )
    ingestion_pipeline.close()
    del ingestion_pipeline

