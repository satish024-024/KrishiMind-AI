"""
Configuration module for Kisan Call Centre Query Assistant
Manages environment variables and application settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
SERVICES_DIR = BASE_DIR / "services"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
EMBEDDINGS_DIR.mkdir(exist_ok=True)
SERVICES_DIR.mkdir(exist_ok=True)

# Data Files
RAW_DATA_FILE = DATA_DIR / "raw_kcc.csv"
CLEAN_DATA_FILE = DATA_DIR / "clean_kcc.csv"
QA_PAIRS_FILE = DATA_DIR / "kcc_qa_pairs.json"

# Embedding Files
EMBEDDINGS_FILE = EMBEDDINGS_DIR / "kcc_embeddings.pkl"
FAISS_INDEX_FILE = EMBEDDINGS_DIR / "faiss_index.bin"
METADATA_FILE = EMBEDDINGS_DIR / "meta.pkl"

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-001")

# Model Configuration
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2

# FAISS Configuration
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# Application Settings
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "False").lower() == "true"

# LLM Parameters
LLM_MAX_TOKENS = 500
LLM_TEMPERATURE = 0.7
LLM_TOP_P = 0.9

def validate_config():
    """Validate critical configuration settings"""
    issues = []
    
    if not RAW_DATA_FILE.exists():
        issues.append(f"Raw data file not found: {RAW_DATA_FILE}")
    
    if not OFFLINE_MODE:
        if not GEMINI_API_KEY:
            issues.append("GEMINI_API_KEY not set in environment")
    
    return issues

if __name__ == "__main__":
    print("Configuration Summary:")
    print(f"Base Directory: {BASE_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Embeddings Directory: {EMBEDDINGS_DIR}")
    print(f"Model: {GEMINI_MODEL_NAME}")
    print(f"Offline Mode: {OFFLINE_MODE}")
    
    issues = validate_config()
    if issues:
        print("\n Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n Configuration validated successfully")
