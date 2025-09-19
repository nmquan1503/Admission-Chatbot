from .base_embedder import BaseEmbedder
from sentence_transformers import SentenceTransformer
from typing import List

class HuggingFaceEmbedder(BaseEmbedder):

    def __init__(self, model_name):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
 
    def embed(self, text: str) -> List[float]:
        return self.model.encode(text, normalize_embeddings=True, convert_to_numpy=True).tolist()
    
    def embed_batch(self, texts: List[str], batch_size:int = 32) -> List[List[float]]:
        embeddings = []
        for i in range(0, len(texts), batch_size):
            embeddings.extend(self.model.encode(
                texts[i : i + batch_size], 
                normalize_embeddings=True, 
                convert_to_numpy=True
            ).tolist())
        return embeddings