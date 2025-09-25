from .ingestion.pipeline import IngestionPipeline
from .config import settings
from fastapi import FastAPI
from .api import chat, session
from fastapi.middleware.cors import CORSMiddleware

if settings.INGESTION_CONFIG['run']:
    ingestion_pipeline = IngestionPipeline()
    ingestion_pipeline.run(
        links_paths=settings.INGESTION_CONFIG['link_paths'],
        pdf_paths=settings.INGESTION_CONFIG['pdf_paths'],
        faq_paths=settings.INGESTION_CONFIG['faq_paths']
    )
    ingestion_pipeline.close()
    del ingestion_pipeline

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat.router, prefix='/chat')
app.include_router(session.router, prefix='/sessions')