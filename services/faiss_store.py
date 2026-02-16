"""
FAISS Vector Store Module
Creates and manages FAISS index for semantic search
"""

import pickle
import numpy as np
import faiss
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config import EMBEDDINGS_FILE, FAISS_INDEX_FILE, METADATA_FILE, EMBEDDING_DIMENSION


def create_faiss_index(
    embeddings_file=EMBEDDINGS_FILE,
    index_file=FAISS_INDEX_FILE,
    metadata_file=METADATA_FILE
):
    """
    Create FAISS index from embeddings
    
    Args:
        embeddings_file: Path to embeddings pickle file
        index_file: Path to save FAISS index
        metadata_file: Path to save metadata
    """
    print(f"[INFO] Loading embeddings from: {embeddings_file}")
    
    # Check if file exists
    if not Path(embeddings_file).exists():
        print(f"[ERROR] File not found - {embeddings_file}")
        print("Please run generate_embeddings.py first")
        return False
    
    # Load embeddings
    with open(embeddings_file, "rb") as f:
        embedded_records = pickle.load(f)
    
    print(f"[SUCCESS] Loaded {len(embedded_records)} embedded records")
    
    # Extract embeddings and metadata
    print("[INFO] Extracting embeddings and metadata...")
    embeddings = []
    metadata = []
    
    for record in embedded_records:
        embeddings.append(record["embedding"])
        metadata.append(record["metadata"])
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings).astype('float32')
    
    print(f"[SUCCESS] Embeddings shape: {embeddings_array.shape}")
    
    # Create FAISS index
    print("[INFO] Creating FAISS index...")
    dimension = embeddings_array.shape[1]
    
    # Use IndexFlatL2 for exact search (good for small to medium datasets)
    index = faiss.IndexFlatL2(dimension)
    
    # Add vectors to index
    index.add(embeddings_array)
    
    print(f"[SUCCESS] FAISS index created with {index.ntotal} vectors")
    
    # Ensure output directory exists
    Path(index_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Save FAISS index
    print("[INFO] Saving FAISS index...")
    faiss.write_index(index, str(index_file))
    print(f"[SUCCESS] FAISS index saved to: {index_file}")
    
    # Save metadata
    print("[INFO] Saving metadata...")
    with open(metadata_file, "wb") as f:
        pickle.dump(metadata, f)
    print(f"[SUCCESS] Metadata saved to: {metadata_file}")
    
    # Print statistics
    print("\n[INFO] FAISS Index Statistics:")
    print(f"  Total vectors: {index.ntotal}")
    print(f"  Dimension: {dimension}")
    print(f"  Index file size: {Path(index_file).stat().st_size / (1024*1024):.2f} MB")
    print(f"  Metadata file size: {Path(metadata_file).stat().st_size / (1024*1024):.2f} MB")
    
    return True


class FAISSSearcher:
    """FAISS-based semantic search"""
    
    def __init__(self, index_file=FAISS_INDEX_FILE, metadata_file=METADATA_FILE):
        """Initialize FAISS searcher"""
        self.index_file = index_file
        self.metadata_file = metadata_file
        self.index = None
        self.metadata = None
        self.model = None
        
    def load(self):
        """Load FAISS index and metadata"""
        # Load FAISS index
        if not Path(self.index_file).exists():
            raise FileNotFoundError(f"FAISS index not found: {self.index_file}")
        
        self.index = faiss.read_index(str(self.index_file))
        
        # Load metadata
        if not Path(self.metadata_file).exists():
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_file}")
        
        with open(self.metadata_file, "rb") as f:
            self.metadata = pickle.load(f)
        
        # Load sentence transformer model for query embedding
        from sentence_transformers import SentenceTransformer
        from config import SENTENCE_TRANSFORMER_MODEL
        
        self.model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        
        return self
    
    def search(self, query, top_k=5, max_distance=1.3):
        """
        Search for similar Q&A pairs
        
        Args:
            query: User query string
            top_k: Number of results to return
            max_distance: Maximum L2 distance threshold. Results beyond this
                         are considered irrelevant and excluded. Default 1.5.
            
        Returns:
            List of dicts with distance, confidence, and metadata
        """
        if self.index is None or self.metadata is None or self.model is None:
            raise RuntimeError("Searcher not loaded. Call load() first.")
        
        # Embed query
        query_embedding = self.model.encode([query]).astype('float32')
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Retrieve results with relevance filtering
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                distance = float(dist)
                # Skip results beyond max_distance threshold
                if distance > max_distance:
                    continue
                # Compute confidence: 1.0 = perfect match, 0.0 = at threshold
                confidence = max(0.0, 1.0 - (distance / max_distance))
                results.append({
                    'distance': distance,
                    'confidence': round(confidence, 2),
                    'metadata': self.metadata[idx]
                })
        
        return results


if __name__ == "__main__":
    print("=" * 60)
    print("Kisan Call Centre - FAISS Index Creation")
    print("=" * 60)
    
    success = create_faiss_index()
    
    if success:
        print("\n[SUCCESS] FAISS index creation completed successfully!")
        
        # Test search
        print("\n" + "=" * 60)
        print("Testing FAISS Search")
        print("=" * 60)
        
        try:
            searcher = FAISSSearcher().load()
            
            test_query = "How to control aphids in mustard?"
            print(f"\n[INFO] Test Query: {test_query}")
            
            results = searcher.search(test_query, top_k=3)
            
            print(f"\n[INFO] Top {len(results)} Results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Distance: {result['distance']:.4f}")
                print(f"   Question: {result['metadata']['question'][:100]}...")
                print(f"   Answer: {result['metadata']['answer'][:100]}...")
        
        except Exception as e:
            print(f"\n[WARNING] Test search failed: {e}")
    else:
        print("\n[ERROR] FAISS index creation failed!")
        sys.exit(1)
