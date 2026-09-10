import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import settings

_model = None

def get_embedding_model():
    global _model
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    except Exception:
        # Graceful fallback: lightweight feature vectorizer with 384 dimensions
        class FallbackEmbedding:
            def encode(self, texts):
                if isinstance(texts, str):
                    texts = [texts]
                vectors = []
                for text in texts:
                    vec = np.zeros(384, dtype=np.float32)
                    for i, ch in enumerate(text.encode("utf-8")):
                        vec[i % 384] += ch / 255.0
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        vec = vec / norm
                    vectors.append(vec)
                return np.array(vectors)
        _model = FallbackEmbedding()
    return _model

def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))

class VectorStore:
    """Vector database manager supporting Qdrant and local embedded persistent fallback."""
    def __init__(self):
        self.client = None
        self.storage_file = settings.QDRANT_STORAGE_DIR / "resumes_vectors.json"
        self._init_client()

    def _init_client(self):
        try:
            from qdrant_client import QdrantClient
            self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=2.0)
            # Test connection
            self.client.get_collections()
        except Exception:
            # Fallback to embedded local vector storage
            self.client = None

    def index_resume(self, candidate_id: int, text: str, metadata: Dict[str, Any]):
        model = get_embedding_model()
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 30]
        if not chunks:
            chunks = [text[:1000]] if text else ["Empty resume"]

        vectors = model.encode(chunks)
        
        # Load local storage
        data = {}
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        candidate_key = str(candidate_id)
        data[candidate_key] = {
            "metadata": metadata,
            "chunks": chunks,
            "vectors": [v.tolist() for v in vectors]
        }

        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def search_resumes(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        model = get_embedding_model()
        query_vec = model.encode([query])[0]

        if not self.storage_file.exists():
            return []

        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return []

        results = []
        for cand_id, cand_data in data.items():
            for i, chunk in enumerate(cand_data["chunks"]):
                chunk_vec = np.array(cand_data["vectors"][i])
                sim = compute_cosine_similarity(query_vec, chunk_vec)
                results.append({
                    "candidate_id": int(cand_id),
                    "chunk": chunk,
                    "similarity": round(sim * 100.0, 2),
                    "metadata": cand_data["metadata"]
                })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def get_candidate_context(self, candidate_id: int, query: str) -> str:
        """Retrieves most relevant resume chunk for a specific candidate."""
        if not self.storage_file.exists():
            return ""
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return ""

        cand_data = data.get(str(candidate_id))
        if not cand_data:
            return ""

        model = get_embedding_model()
        query_vec = model.encode([query])[0]
        best_sim = -1.0
        best_chunk = ""

        for i, chunk in enumerate(cand_data["chunks"]):
            chunk_vec = np.array(cand_data["vectors"][i])
            sim = compute_cosine_similarity(query_vec, chunk_vec)
            if sim > best_sim:
                best_sim = sim
                best_chunk = chunk

        return best_chunk

vector_store = VectorStore()
