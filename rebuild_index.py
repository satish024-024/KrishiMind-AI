"""
Rebuild FAISS Index from Large KCC Dataset
Processes kcc_dataset.csv (7.3GB) to extract QA pairs and rebuild embeddings
"""

import csv
import json
import pickle
import numpy as np
import sys
from pathlib import Path

# Add parent for config imports
sys.path.append(str(Path(__file__).parent))
from config import (
    DATA_DIR, EMBEDDINGS_DIR,
    FAISS_INDEX_FILE, METADATA_FILE, EMBEDDINGS_FILE,
    SENTENCE_TRANSFORMER_MODEL, EMBEDDING_DIMENSION
)

LARGE_CSV = DATA_DIR / "kcc_dataset.csv"
QA_OUTPUT = DATA_DIR / "kcc_qa_pairs.json"
MAX_PAIRS = 2000  # Limit for reasonable memory usage


def extract_qa_pairs(csv_path, max_pairs=MAX_PAIRS):
    """Extract unique Q&A pairs from the large CSV"""
    print(f"[INFO] Reading CSV: {csv_path}")
    print(f"[INFO] Max pairs to extract: {max_pairs}")

    qa_pairs = []
    seen_questions = set()
    skipped = 0
    total = 0

    with open(csv_path, encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if total % 500_000 == 0:
                print(f"  ... processed {total:,} rows, extracted {len(qa_pairs)} pairs")

            question = (row.get('QueryText') or '').strip()
            answer = (row.get('KccAns') or '').strip()

            # Skip empty or very short Q&A
            if len(question) < 10 or len(answer) < 10:
                skipped += 1
                continue

            # Deduplicate by question text (case-insensitive)
            q_key = question.lower()
            if q_key in seen_questions:
                continue
            seen_questions.add(q_key)

            qa_pairs.append({
                "question": question,
                "answer": answer,
                "metadata": {
                    "state": (row.get('StateName') or '').strip().title(),
                    "district": (row.get('DistrictName') or '').strip().title(),
                    "crop": (row.get('Crop') or '').strip().title(),
                    "category": (row.get('Category') or '').strip().title(),
                    "query_type": (row.get('QueryType') or '').strip(),
                    "season": (row.get('Season') or '').strip().title()
                }
            })

            if len(qa_pairs) >= max_pairs:
                print(f"[INFO] Reached max pairs limit ({max_pairs})")
                break

    print(f"\n[DONE] Processed {total:,} rows total")
    print(f"  Extracted: {len(qa_pairs)} unique Q&A pairs")
    print(f"  Skipped: {skipped:,} (empty/short)")
    return qa_pairs


def save_qa_pairs(qa_pairs, output_path):
    """Save QA pairs to JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
    print(f"[SAVED] QA pairs → {output_path} ({len(qa_pairs)} entries)")


def generate_embeddings(qa_pairs):
    """Generate sentence embeddings for all QA pairs"""
    from sentence_transformers import SentenceTransformer

    print(f"\n[INFO] Loading model: {SENTENCE_TRANSFORMER_MODEL}")
    model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)

    # Combine question + answer for richer embeddings
    texts = [f"{qa['question']} {qa['answer']}" for qa in qa_pairs]

    print(f"[INFO] Generating embeddings for {len(texts)} texts...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
    print(f"[DONE] Embeddings shape: {embeddings.shape}")

    # Package as records
    records = []
    for i, qa in enumerate(qa_pairs):
        records.append({
            "embedding": embeddings[i],
            "metadata": qa
        })

    return records, embeddings


def build_faiss_index(embeddings, records):
    """Build and save FAISS index"""
    import faiss

    embeddings_array = np.array(embeddings).astype('float32')
    dimension = embeddings_array.shape[1]

    print(f"\n[INFO] Building FAISS index (dim={dimension}, n={len(embeddings_array)})")
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    print(f"[DONE] Index has {index.ntotal} vectors")

    # Save index
    EMBEDDINGS_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_FILE))
    print(f"[SAVED] FAISS index → {FAISS_INDEX_FILE}")

    # Save metadata
    metadata = [r["metadata"] for r in records]
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(metadata, f)
    print(f"[SAVED] Metadata → {METADATA_FILE}")

    # Save embeddings
    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump(records, f)
    print(f"[SAVED] Embeddings → {EMBEDDINGS_FILE}")

    # Stats
    idx_size = Path(FAISS_INDEX_FILE).stat().st_size / (1024*1024)
    meta_size = Path(METADATA_FILE).stat().st_size / (1024*1024)
    print(f"\n[STATS] Index: {idx_size:.2f} MB | Metadata: {meta_size:.2f} MB")


def main():
    print("=" * 60)
    print("KrishiMind AI — Rebuild FAISS Index")
    print("=" * 60)

    if not LARGE_CSV.exists():
        print(f"\n[ERROR] Dataset not found: {LARGE_CSV}")
        print("Please place kcc_dataset.csv in the data/ folder")
        sys.exit(1)

    # Step 1: Extract QA pairs
    qa_pairs = extract_qa_pairs(LARGE_CSV)

    # Step 2: Save QA pairs
    save_qa_pairs(qa_pairs, QA_OUTPUT)

    # Step 3: Generate embeddings
    records, embeddings = generate_embeddings(qa_pairs)

    # Step 4: Build FAISS index
    build_faiss_index(embeddings, records)

    print("\n" + "=" * 60)
    print("[SUCCESS] FAISS index rebuilt with enriched dataset!")
    print(f"  Total Q&A pairs: {len(qa_pairs)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
