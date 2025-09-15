from .base_embedder import BaseEmbedder
from sentence_transformers import SentenceTransformer
from typing import List

class HuggingFaceEmbedder(BaseEmbedder):

    def __init__(self, model_name):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
 
    def embed(self, text: str) -> List[float]:
        return self.model.encode(text, normalize_embeddings=True, convert_to_numpy=True).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True, convert_to_numpy=True).tolist()