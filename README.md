# Kisan Call Centre Query Assistant

A production-ready AI-powered agricultural helpdesk system using IBM Watsonx Granite LLM and FAISS vector search to answer farmers' queries related to crop diseases, pest control, fertilizer usage, and government schemes.

## Overview

The Kisan Call Centre Query Assistant is an intelligent agricultural query resolution system designed for rural support and information dissemination. It leverages advanced AI capabilities to provide accurate, contextual answers to agricultural queries in both offline and online modes.

### Key Features

- **Dual Mode Operation**: Works in both offline (FAISS-only) and online (LLM-enhanced) modes
- **Semantic Search**: Uses FAISS vector similarity search for accurate query matching
- **AI-Enhanced Responses**: Integrates IBM Watsonx Granite LLM for natural language generation
- **Multilingual Support**: Handles queries and answers in both English and Hindi
- **Production-Ready**: Professional UI, error handling, and scalable architecture

## Technical Architecture

### Technology Stack

- **Backend**: Python 3.9+
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **LLM**: IBM Watsonx Granite (ibm/granite-3-8b-instruct)
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy

### System Workflow

1. **Data Preprocessing**: Clean and extract Q&A pairs from raw KCC dataset
2. **Embedding Generation**: Convert Q&A pairs to vector embeddings
3. **FAISS Indexing**: Create searchable vector index
4. **Query Processing**: Embed user queries and perform similarity search
5. **Response Generation**: Return offline answers and optionally generate LLM-enhanced responses

## Installation

### Prerequisites

- Python 3.9 or higher
- IBM Cloud account with Watsonx enabled (for online mode)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd krishi-mitra-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your IBM Watsonx credentials:
   ```
   IBM_WATSONX_API_KEY=your_api_key_here
   IBM_WATSONX_PROJECT_ID=your_project_id_here
   IBM_WATSONX_URL=https://eu-de.ml.cloud.ibm.com
   MODEL_NAME=ibm/granite-3-8b-instruct
   ```

5. **Place dataset**
   
   Add your `raw_kcc.csv` file to the `data/` directory

6. **Run setup verification**
   ```bash
   python setup.py
   ```

## Data Preparation

### Step 1: Data Preprocessing

Clean the raw KCC dataset and extract Q&A pairs:

```bash
python services/data_preprocessing.py
```

This will create:
- `data/clean_kcc.csv` - Cleaned dataset
- `data/kcc_qa_pairs.json` - Extracted Q&A pairs

### Step 2: Generate Embeddings

Create vector embeddings for all Q&A pairs:

```bash
python services/generate_embeddings.py
```

This will create:
- `embeddings/kcc_embeddings.pkl` - Vector embeddings with metadata

### Step 3: Build FAISS Index

Create the FAISS search index:

```bash
python services/faiss_store.py
```

This will create:
- `embeddings/faiss_index.bin` - FAISS vector index
- `embeddings/meta.pkl` - Metadata mapping

## Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Usage

### Offline Mode

- Disable "Enable Online Mode" in the sidebar
- Queries are answered using FAISS similarity search only
- Works without internet connectivity or IBM Watsonx credentials

### Online Mode

- Enable "Enable Online Mode" in the sidebar
- Queries are enhanced with IBM Watsonx Granite LLM
- Provides contextual, natural language responses

### Sample Queries

1. How to control aphids in mustard?
2. What is the treatment for leaf spot in tomato?
3. Suggest pesticide for whitefly in cotton.
4. How to prevent fruit borer in brinjal?
5. What fertilizer is recommended during flowering in maize?
6. How to protect paddy from blast disease?
7. What is the solution for jassids in cotton?
8. How to apply for PM Kisan Samman Nidhi scheme?
9. What is the dosage of neem oil for aphids?
10. How to treat blight in potato crops?

## Project Structure

```
krishi-mitra-ai/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration management
├── setup.py                        # Setup verification script
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── data/
│   ├── raw_kcc.csv                # Raw KCC dataset
│   ├── clean_kcc.csv              # Cleaned dataset
│   └── kcc_qa_pairs.json          # Extracted Q&A pairs
├── embeddings/
│   ├── kcc_embeddings.pkl         # Vector embeddings
│   ├── faiss_index.bin            # FAISS index
│   └── meta.pkl                   # Metadata mapping
└── services/
    ├── data_preprocessing.py      # Data cleaning module
    ├── generate_embeddings.py     # Embedding generation
    ├── faiss_store.py             # FAISS indexing
    ├── watsonx_service.py         # IBM Watsonx integration
    └── query_handler.py           # Query processing pipeline
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `IBM_WATSONX_API_KEY` | IBM Watsonx API key | - |
| `IBM_WATSONX_PROJECT_ID` | IBM Watsonx project ID | - |
| `IBM_WATSONX_URL` | IBM Watsonx endpoint URL | `https://eu-de.ml.cloud.ibm.com` |
| `MODEL_NAME` | LLM model identifier | `ibm/granite-3-8b-instruct` |
| `TOP_K_RESULTS` | Number of similar results | `5` |
| `OFFLINE_MODE` | Force offline mode | `False` |

### Model Parameters

- **Sentence Transformer**: `all-MiniLM-L6-v2` (384 dimensions)
- **FAISS Index**: IndexFlatL2 (exact search)
- **LLM Temperature**: 0.7
- **LLM Max Tokens**: 500

## API Reference

### FAISSSearcher

```python
from services.faiss_store import FAISSSearcher

searcher = FAISSSearcher().load()
results = searcher.search(query="How to control aphids?", top_k=5)
```

### WatsonxService

```python
from services.watsonx_service import WatsonxService

service = WatsonxService().initialize()
response = service.answer_query(query, context_qa_pairs)
```

### QueryHandler

```python
from services.query_handler import QueryHandler

handler = QueryHandler(faiss_searcher, watsonx_service)
result = handler.process_query(query, top_k=5, online_mode=True)
```

## Performance Considerations

- **Embedding Generation**: ~1-2 minutes for 10,000 Q&A pairs
- **FAISS Indexing**: < 1 second for 10,000 vectors
- **Query Search**: < 100ms per query
- **LLM Response**: 2-5 seconds (depends on network and API)

## Deployment

### Production Checklist

- [ ] Set strong API keys in environment variables
- [ ] Enable HTTPS for Streamlit
- [ ] Configure proper logging
- [ ] Set up monitoring and alerting
- [ ] Implement rate limiting for API calls
- [ ] Add authentication for the web interface
- [ ] Configure backup for embeddings and index files

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Troubleshooting

### Common Issues

**Issue**: FAISS index not found
- **Solution**: Run the data preparation scripts in order

**Issue**: IBM Watsonx authentication failed
- **Solution**: Verify API key and project ID in `.env` file

**Issue**: Out of memory during embedding generation
- **Solution**: Reduce batch size in `generate_embeddings.py`

**Issue**: Slow query responses
- **Solution**: Reduce `top_k` value or optimize FAISS index type

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Kisan Call Centre for the agricultural dataset
- IBM Watsonx for the Granite LLM
- Facebook AI Research for FAISS
- Sentence Transformers team for the embedding models

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

---

**Built with the goal of empowering farmers through AI-driven agricultural knowledge dissemination.**
