"""
Setup Script for Kisan Call Centre Query Assistant
Initializes project structure and verifies dependencies
"""

import sys
from pathlib import Path
import subprocess

# Add current directory to path
sys.path.append(str(Path(__file__).parent))


def create_directories():
    """Create necessary directories"""
    print("[INFO] Creating directory structure...")
    
    directories = [
        "data",
        "embeddings",
        "services"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"  [SUCCESS] {dir_name}/")
    
    print()


def check_dependencies():
    """Check if required packages are installed"""
    print("[INFO] Checking dependencies...")
    
    required_packages = [
        "streamlit",
        "sentence_transformers",
        "faiss",
        "pandas",
        "numpy",
        "ibm_watsonx_ai",
        "dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  [SUCCESS] {package}")
        except ImportError:
            print(f"  [ERROR] {package} (not installed)")
            missing_packages.append(package)
    
    print()
    
    if missing_packages:
        print("[WARNING] Missing packages detected!")
        print("Install them with: pip install -r requirements.txt")
        print()
        return False
    
    return True


def check_dataset():
    """Check if dataset exists"""
    print("[INFO] Checking dataset...")
    
    from config import RAW_DATA_FILE
    
    if RAW_DATA_FILE.exists():
        print(f"  [SUCCESS] Dataset found: {RAW_DATA_FILE}")
        print()
        return True
    else:
        print(f"  [ERROR] Dataset not found: {RAW_DATA_FILE}")
        print()
        print("[WARNING] Please place your raw_kcc.csv file in the data/ directory")
        print()
        return False


def check_env_file():
    """Check if .env file exists"""
    print("[INFO] Checking environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print(f"  [SUCCESS] .env file found")
        print()
        return True
    else:
        print(f"  [ERROR] .env file not found")
        print()
        
        if env_example.exists():
            print("[INFO] Creating .env from .env.example...")
            env_file.write_text(env_example.read_text())
            print("  [SUCCESS] .env file created")
            print("  [WARNING] Please update it with your IBM Watsonx credentials")
            print()
        else:
            print("[WARNING] Please create a .env file with your IBM Watsonx credentials")
            print()
        
        return False


def check_faiss_index():
    """Check if FAISS index exists"""
    print("[INFO] Checking FAISS index...")
    
    from config import FAISS_INDEX_FILE, METADATA_FILE
    
    if FAISS_INDEX_FILE.exists() and METADATA_FILE.exists():
        print(f"  [SUCCESS] FAISS index found")
        print()
        return True
    else:
        print(f"  [ERROR] FAISS index not found")
        print()
        print("[INFO] Run the following scripts to create the index:")
        print("  1. python services/data_preprocessing.py")
        print("  2. python services/generate_embeddings.py")
        print("  3. python services/faiss_store.py")
        print()
        return False


def main():
    """Main setup function"""
    print("=" * 70)
    print("Kisan Call Centre Query Assistant - Setup")
    print("=" * 70)
    print()
    
    # Create directories
    create_directories()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check dataset
    dataset_ok = check_dataset()
    
    # Check env file
    env_ok = check_env_file()
    
    # Check FAISS index
    faiss_ok = check_faiss_index()
    
    # Summary
    print("=" * 70)
    print("Setup Summary")
    print("=" * 70)
    print()
    
    if deps_ok and dataset_ok and env_ok and faiss_ok:
        print("[SUCCESS] All checks passed! You're ready to run the application.")
        print()
        print("To start the application, run:")
        print("  streamlit run app.py")
    else:
        print("[WARNING] Some checks failed. Please address the issues above.")
        print()
        
        if not deps_ok:
            print("1. Install dependencies: pip install -r requirements.txt")
        
        if not dataset_ok:
            print("2. Place raw_kcc.csv in the data/ directory")
        
        if not env_ok:
            print("3. Configure .env file with IBM Watsonx credentials")
        
        if not faiss_ok:
            print("4. Run preprocessing and indexing scripts:")
            print("   - python services/data_preprocessing.py")
            print("   - python services/generate_embeddings.py")
            print("   - python services/faiss_store.py")
    
    print()


if __name__ == "__main__":
    main()
