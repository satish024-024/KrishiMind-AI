"""
Embedding Generation Module
Generates vector embeddings for Q&A pairs using Sentence Transformers
"""

import json
import pickle
from pathlib import Path
import sys
from sentence_transformers import SentenceTransformer

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config import QA_PAIRS_FILE, EMBEDDINGS_FILE, SENTENCE_TRANSFORMER_MODEL


def generate_embeddings(
    input_json=QA_PAIRS_FILE,
    output_pickle=EMBEDDINGS_FILE,
    model_name=SENTENCE_TRANSFORMER_MODEL
):
    """
    Generate embeddings for Q&A pairs
    
    Args:
        input_json: Path to Q&A pairs JSON file
        output_pickle: Path to save embeddings pickle file
        model_name: Name of the Sentence Transformer model
    """
    print(f"[INFO] Loading Q&A data from: {input_json}")
    
    # Check if file exists
    if not Path(input_json).exists():
        print(f"[ERROR] File not found - {input_json}")
        print("Please run data_preprocessing.py first")
        return False
    
    # Load Q&A data
    with open(input_json, "r", encoding="utf-8") as f:
        qa_data = json.load(f)
    
    print(f"[SUCCESS] Loaded {len(qa_data)} Q&A pairs")
    
    # Initialize Sentence Transformer model
    print(f"[INFO] Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    print(f"[SUCCESS] Model loaded successfully")
    
    # Prepare texts to embed
    # Format: "Q: {question} A: {answer}"
    print("[INFO] Preparing texts for embedding...")
    texts = []
    for item in qa_data:
        text = f"Q: {item['question']} A: {item['answer']}"
        texts.append(text)
    
    # Generate embeddings
    print(f"[INFO] Generating embeddings for {len(texts)} texts...")
    print("   This may take a few minutes...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    print(f"[SUCCESS] Generated embeddings with shape: {embeddings.shape}")
    
    # Save as a list of (embedding, metadata) tuples
    print("[INFO] Saving embeddings...")
    embedded_records = []
    
    for vec, item in zip(embeddings, qa_data):
        embedded_records.append({
            "embedding": vec,
            "metadata": item
        })
    
    # Ensure output directory exists
    Path(output_pickle).parent.mkdir(parents=True, exist_ok=True)
    
    # Save to pickle file
    with open(output_pickle, "wb") as f:
        pickle.dump(embedded_records, f)
    
    print(f"[SUCCESS] Embeddings saved to: {output_pickle}")
    
    # Print statistics
    print("\n[INFO] Embedding Statistics:")
    print(f"  Total embeddings: {len(embedded_records)}")
    print(f"  Embedding dimension: {embeddings.shape[1]}")
    print(f"  File size: {Path(output_pickle).stat().st_size / (1024*1024):.2f} MB")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Kisan Call Centre - Embedding Generation")
    print("=" * 60)
    
    success = generate_embeddings()
    
    if success:
        print("\n[SUCCESS] Embedding generation completed successfully!")
    else:
        print("\n[ERROR] Embedding generation failed!")
        sys.exit(1)
