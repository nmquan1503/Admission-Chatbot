import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'config.yaml'), 'r', encoding='utf-8') as f:
    yaml_config = yaml.safe_load(f)

WEB_LOADER_CONFIG = yaml_config['loaders']['web']
CHARACTER_SPLITTER_CONFIG = yaml_config['splitters']['character_size']

HUGGING_FACE_EMBEDDER_CONFIG = yaml_config['embedders']['hugging_face']

WEAVIATE_CONFIG = yaml_config['vector_stores']['weaviate']

INGESTION_CONFIG = yaml_config['ingestion']

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

SUMMARY_MODEL_NAME = yaml_config['summary']['model_name']

ANSWER_MODEL_NAME = yaml_config['answer']['model_name']

INTENT_CLASSIFICATION_MODEL_NAME = yaml_config['intent_classification']['model_name']