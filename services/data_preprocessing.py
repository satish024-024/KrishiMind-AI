"""
Data Preprocessing Module for Kisan Call Centre Dataset
Cleans raw CSV data and extracts Q&A pairs
"""

import pandas as pd
import json
import re
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config import RAW_DATA_FILE, CLEAN_DATA_FILE, QA_PAIRS_FILE


def clean_text(text):
    """Clean and normalize text"""
    if pd.isna(text):
        return ""
    
    # Convert to string
    text = str(text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def is_valid_qa_pair(query, answer):
    """Validate if Q&A pair is meaningful"""
    # Check if both query and answer exist
    if not query or not answer:
        return False
    
    # Check minimum length
    if len(query) < 10 or len(answer) < 10:
        return False
    
    # Check if answer is not just a placeholder
    placeholder_patterns = [
        r'^NA$',
        r'^N/A$',
        r'^-$',
        r'^\.+$',
    ]
    
    for pattern in placeholder_patterns:
        if re.match(pattern, answer.strip(), re.IGNORECASE):
            return False
    
    return True


def preprocess_kcc_data(input_file=RAW_DATA_FILE, output_csv=CLEAN_DATA_FILE, output_json=QA_PAIRS_FILE):
    """
    Preprocess Kisan Call Centre dataset
    
    Args:
        input_file: Path to raw CSV file
        output_csv: Path to save cleaned CSV
        output_json: Path to save Q&A pairs JSON
    """
    print(f"[INFO] Loading data from: {input_file}")
    
    # Check if file exists
    if not Path(input_file).exists():
        print(f"[ERROR] File not found - {input_file}")
        print("Please place the raw_kcc.csv file in the data/ directory")
        return False
    
    # Load raw data
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        df = pd.read_csv(input_file, encoding='latin-1')
    
    print(f"[SUCCESS] Loaded {len(df)} records")
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Clean text fields
    print("[INFO] Cleaning text fields...")
    text_columns = ['QueryText', 'KccAns', 'StateName', 'DistrictName', 
                    'BlockName', 'Crop', 'QueryType', 'Category']
    
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['QueryText', 'KccAns'], keep='first')
    duplicates_removed = initial_count - len(df)
    print(f"[INFO] Removed {duplicates_removed} duplicate records")
    
    # Extract Q&A pairs
    print("[INFO] Extracting Q&A pairs...")
    qa_pairs = []
    
    for idx, row in df.iterrows():
        query = row.get('QueryText', '')
        answer = row.get('KccAns', '')
        
        if is_valid_qa_pair(query, answer):
            qa_pair = {
                'question': query,
                'answer': answer,
                'metadata': {
                    'state': row.get('StateName', ''),
                    'district': row.get('DistrictName', ''),
                    'crop': row.get('Crop', ''),
                    'category': row.get('Category', ''),
                    'query_type': row.get('QueryType', ''),
                    'season': row.get('Season', ''),
                }
            }
            qa_pairs.append(qa_pair)
    
    print(f"[SUCCESS] Extracted {len(qa_pairs)} valid Q&A pairs")
    
    # Save cleaned CSV
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"[SUCCESS] Saved cleaned data to: {output_csv}")
    
    # Save Q&A pairs as JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] Saved Q&A pairs to: {output_json}")
    
    # Print statistics
    print("\n[INFO] Data Statistics:")
    print(f"  Total records: {len(df)}")
    print(f"  Valid Q&A pairs: {len(qa_pairs)}")
    print(f"  Unique crops: {df['Crop'].nunique() if 'Crop' in df.columns else 'N/A'}")
    print(f"  Unique states: {df['StateName'].nunique() if 'StateName' in df.columns else 'N/A'}")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Kisan Call Centre - Data Preprocessing")
    print("=" * 60)
    
    success = preprocess_kcc_data()
    
    if success:
        print("\n[SUCCESS] Data preprocessing completed successfully!")
    else:
        print("\n[ERROR] Data preprocessing failed!")
        sys.exit(1)
