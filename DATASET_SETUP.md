# Using Your KCC Dataset - Quick Start Guide

## Overview

This guide will help you set up the Kisan Call Centre Query Assistant with your actual KCC dataset and IBM Watsonx AI.

## Prerequisites

✅ Python 3.9 or higher installed  
✅ Your KCC dataset CSV file  
✅ IBM Cloud account with Watsonx access  
✅ IBM Watsonx API key and Project ID  

## Quick Setup (3 Steps)

### Step 1: Place Your Dataset

1. Copy your KCC dataset CSV file to the `data/` folder
2. Rename it to `raw_kcc.csv`
3. Your file should be at: `data/raw_kcc.csv`

**Expected CSV Format:**
```csv
StateName,DistrictName,BlockName,Season,Sector,Category,Crop,QueryType,QueryText,KccAns,CreatedOn,year,month
Uttar Pradesh,Agra,ETMADPUR,,HORTICULTURE,Vegetables,Potato,Plant Protection,Which medicine should be used for late blight in potato?,For late blight control in potato spray Mancozeb...,2024-01-01,2024,1
```

### Step 2: Configure IBM Watsonx

1. **Get your credentials** (see `IBM_WATSONX_SETUP.md` for detailed instructions):
   - IBM Cloud API Key
   - Watsonx Project ID

2. **Update `.env` file**:
   ```bash
   # Open .env in a text editor
   notepad .env
   ```

3. **Add your credentials**:
   ```
   IBM_WATSONX_API_KEY=your_actual_api_key_here
   IBM_WATSONX_PROJECT_ID=your_actual_project_id_here
   IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
   MODEL_NAME=ibm/granite-3-8b-instruct
   ```

### Step 3: Run Quick Setup

```bash
python quick_setup.py
```

This will automatically:
- ✅ Clean and preprocess your data
- ✅ Generate vector embeddings
- ✅ Create FAISS search index

**Note**: Embedding generation may take 5-15 minutes depending on your dataset size.

## Manual Setup (Alternative)

If you prefer to run each step manually:

```bash
# Step 1: Preprocess data
python services/data_preprocessing.py

# Step 2: Generate embeddings (may take several minutes)
python services/generate_embeddings.py

# Step 3: Create FAISS index
python services/faiss_store.py
```

## Running the Application

Once setup is complete:

```bash
streamlit run app.py
```

The app will open in your browser at: `http://localhost:8501`

## Dataset Requirements

Your CSV file should include these columns:

| Column | Description | Required |
|--------|-------------|----------|
| `QueryText` | The farmer's question | ✅ Yes |
| `KccAns` | The answer from KCC | ✅ Yes |
| `Crop` | Crop name | ⚠️ Recommended |
| `StateName` | State | ⚠️ Recommended |
| `Category` | Query category | ⚠️ Recommended |

**Minimum Required Columns**: `QueryText` and `KccAns`

## Expected Processing Times

Based on dataset size:

| Records | Preprocessing | Embeddings | FAISS Index | Total |
|---------|--------------|------------|-------------|-------|
| 1,000 | ~10 seconds | ~30 seconds | ~1 second | ~1 minute |
| 10,000 | ~30 seconds | ~3 minutes | ~2 seconds | ~4 minutes |
| 50,000 | ~2 minutes | ~15 minutes | ~5 seconds | ~17 minutes |
| 100,000+ | ~5 minutes | ~30 minutes | ~10 seconds | ~35 minutes |

## Verifying Your Setup

### 1. Check Data Processing

After preprocessing, you should have:
```
data/
├── raw_kcc.csv          (your original file)
├── clean_kcc.csv        (cleaned data)
└── kcc_qa_pairs.json    (extracted Q&A pairs)
```

### 2. Check Embeddings

After embedding generation:
```
embeddings/
└── kcc_embeddings.pkl   (vector embeddings)
```

### 3. Check FAISS Index

After index creation:
```
embeddings/
├── kcc_embeddings.pkl
├── faiss_index.bin      (search index)
└── meta.pkl             (metadata)
```

## Testing the System

### Test Offline Mode (FAISS only)

1. Open the app: `streamlit run app.py`
2. In the sidebar, **disable** "Enable AI Enhancement"
3. Try a sample query:
   ```
   How to control aphids in mustard?
   ```
4. You should see results from your KCC database

### Test Online Mode (with IBM Watsonx)

1. Make sure your `.env` has valid credentials
2. In the sidebar, **enable** "Enable AI Enhancement"
3. Try the same query
4. You should see both:
   - Database Answer (from FAISS)
   - AI-Enhanced Answer (from Granite LLM)

## Troubleshooting

### Issue: "No dataset found"
**Solution**: Make sure your file is at `data/raw_kcc.csv` (exact name and location)

### Issue: "Invalid CSV format"
**Solution**: 
- Check that your CSV has `QueryText` and `KccAns` columns
- Ensure the file is properly formatted CSV (not Excel)
- Try opening in Excel and saving as CSV again

### Issue: "Out of memory during embedding generation"
**Solution**:
- Close other applications
- Process in batches by editing `services/generate_embeddings.py`
- Reduce batch size from 32 to 16 or 8

### Issue: "IBM Watsonx authentication failed"
**Solution**:
- Verify your API key in `.env` (no extra spaces)
- Check your Project ID is correct
- Ensure your IBM Cloud account has Watsonx access
- See `IBM_WATSONX_SETUP.md` for detailed troubleshooting

### Issue: "Model not found"
**Solution**:
- Try a different model in `.env`:
  ```
  MODEL_NAME=ibm/granite-13b-chat-v2
  ```
- Check available models in your Watsonx project

## Dataset Statistics

After processing, check the statistics:

```bash
python services/data_preprocessing.py
```

Look for output like:
```
[SUCCESS] Loaded 50,000 records
[SUCCESS] Extracted 45,000 Q&A pairs
[SUCCESS] Saved to data/kcc_qa_pairs.json
```

## Performance Optimization

### For Large Datasets (100,000+ records)

1. **Use GPU for embeddings** (if available):
   - Edit `services/generate_embeddings.py`
   - Change device from 'cpu' to 'cuda'

2. **Increase batch size**:
   - Edit `services/generate_embeddings.py`
   - Change batch_size from 32 to 64 or 128

3. **Use FAISS GPU** (if available):
   ```bash
   pip uninstall faiss-cpu
   pip install faiss-gpu
   ```

## Next Steps

Once your system is running:

1. ✅ Test with various agricultural queries
2. ✅ Monitor response quality
3. ✅ Collect user feedback
4. ✅ Fine-tune prompts in `services/watsonx_service.py`
5. ✅ Add more sample queries in the sidebar

## Need Help?

- 📖 See `README.md` for full documentation
- 🔧 See `IBM_WATSONX_SETUP.md` for Watsonx configuration
- 🐛 Check `setup.py` for system verification
- 💬 Open an issue on GitHub

## Security Reminder

⚠️ **Never commit your `.env` file to version control!**

The `.gitignore` file is already configured to exclude:
- `.env` (your credentials)
- `data/raw_kcc.csv` (your dataset)
- `embeddings/*.pkl` (generated files)

---

**Ready to help farmers with AI-powered agricultural knowledge!** 🌾
