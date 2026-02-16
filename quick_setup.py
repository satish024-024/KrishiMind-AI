"""
Quick Setup Script for Kisan Call Centre Query Assistant
This script helps you set up your actual KCC dataset
"""

import os
from pathlib import Path

def main():
    print("=" * 70)
    print("Kisan Call Centre Query Assistant - Quick Setup")
    print("=" * 70)
    print()
    
    # Check if raw dataset exists
    raw_data = Path("data/raw_kcc.csv")
    
    if not raw_data.exists():
        print("[INFO] No dataset found at data/raw_kcc.csv")
        print()
        print("Please follow these steps:")
        print()
        print("1. Place your KCC dataset CSV file in the data/ folder")
        print("   - File should be named: raw_kcc.csv")
        print("   - Location: data/raw_kcc.csv")
        print()
        print("2. Your CSV should have these columns:")
        print("   - StateName, DistrictName, BlockName, Season, Sector")
        print("   - Category, Crop, QueryType, QueryText, KccAns")
        print("   - CreatedOn, year, month")
        print()
        print("3. After placing the file, run this script again:")
        print("   python quick_setup.py")
        print()
        return
    
    print(f"[SUCCESS] Found dataset: {raw_data}")
    print()
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("[INFO] Creating .env file from template...")
        env_example = Path(".env.example")
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("[SUCCESS] Created .env file")
            print()
            print("[ACTION REQUIRED] Please update .env with your IBM Watsonx credentials:")
            print("  1. Open .env file in a text editor")
            print("  2. Add your IBM_WATSONX_API_KEY")
            print("  3. Add your IBM_WATSONX_PROJECT_ID")
            print()
            print("  See IBM_WATSONX_SETUP.md for detailed instructions")
            print()
    else:
        print("[SUCCESS] .env file exists")
        print()
    
    # Ask user if they want to proceed with data processing
    print("=" * 70)
    print("Ready to process your dataset!")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Clean and preprocess your KCC data")
    print("  2. Generate vector embeddings (may take a few minutes)")
    print("  3. Create FAISS search index")
    print()
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print()
        print("=" * 70)
        print("Step 1/3: Data Preprocessing")
        print("=" * 70)
        os.system("python services/data_preprocessing.py")
        
        print()
        print("=" * 70)
        print("Step 2/3: Generating Embeddings")
        print("=" * 70)
        print("[INFO] This may take several minutes depending on dataset size...")
        os.system("python services/generate_embeddings.py")
        
        print()
        print("=" * 70)
        print("Step 3/3: Creating FAISS Index")
        print("=" * 70)
        os.system("python services/faiss_store.py")
        
        print()
        print("=" * 70)
        print("Setup Complete!")
        print("=" * 70)
        print()
        print("To start the application, run:")
        print("  streamlit run app.py")
        print()
        print("The app will be available at: http://localhost:8501")
        print()
    else:
        print()
        print("[INFO] Setup cancelled. Run this script again when ready.")
        print()

if __name__ == "__main__":
    main()
