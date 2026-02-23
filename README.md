# 🌾 KrishiMind AI — Smart Agriculture Assistant

> **AI-powered agricultural advisor for Indian farmers.** Get instant answers about crop management, pest control, weather, market prices, and farming best practices — powered by Google Gemini AI + FAISS semantic search over 2,000+ verified KCC (Kisan Call Centre) Q&A pairs.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?logo=streamlit)
![Flask](https://img.shields.io/badge/Flask-API-black?logo=flask)
![Gemini](https://img.shields.io/badge/Google_Gemini-AI-orange?logo=google)
![FAISS](https://img.shields.io/badge/FAISS-Search-green)
![TailwindCSS](https://img.shields.io/badge/Tailwind-Dashboard-06B6D4?logo=tailwindcss)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Running the Application](#-running-the-application)
- [API Reference](#-api-reference)
- [How It Works](#-how-it-works)
- [Dataset Information](#-dataset-information)
- [Configuration](#-configuration)
- [Branches](#-branches)
- [Contributing](#-contributing)
- [Team](#-team)

---

## 🌟 Overview

**KrishiMind AI** is an intelligent agricultural assistant designed specifically for Indian farmers. It combines:

1. **FAISS Semantic Search** — Searches through 2,000+ verified Q&A pairs from India's Kisan Call Centre (KCC) dataset to find the most relevant answers.
2. **Google Gemini AI** — Enhances results with AI-generated explanations and handles general queries that aren't in the knowledge base.
3. **Multi-language Support** — Supports English, Hindi (हिन्दी), Marathi (मराठी), Telugu (తెలుగు), Tamil (தமிழ்), Kannada (ಕನ್ನಡ), Bengali (বাংলা), and Gujarati (ગુજરાતી).

### Problem Statement

Indian farmers often lack access to timely, accurate agricultural information. KrishiMind AI solves this by providing:
- Instant answers to farming questions
- AI-powered crop and pest advice
- Information derived from verified government (KCC) data
- Access in regional languages

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                        │
│                                                                │
│   ┌─────────────────┐        ┌──────────────────────────┐     │
│   │  Streamlit UI    │        │  HTML/Tailwind Dashboard  │    │
│   │  (app.py)        │        │  (dashboard/index.html)   │    │
│   │  Port: 8501      │        │  Port: 5000/dashboard/    │    │
│   └────────┬─────────┘        └────────────┬─────────────┘    │
│            │                                │                  │
│    Direct import                     REST API calls            │
│            │                                │                  │
│            ▼                                ▼                  │
│   ┌─────────────────────────────────────────────────────┐     │
│   │              BACKEND SERVICES (shared)               │     │
│   │                                                       │     │
│   │  ┌──────────────┐  ┌───────────────┐  ┌──────────┐  │     │
│   │  │ FAISS Store   │  │ Query Handler │  │ Gemini   │  │     │
│   │  │ (faiss_store) │  │ (query_handler│  │ Service  │  │     │
│   │  │               │  │  .py)         │  │ (watsonx │  │     │
│   │  │ Semantic      │  │               │  │ _service │  │     │
│   │  │ Search        │  │ Orchestrates  │  │  .py)    │  │     │
│   │  │ over 2000+    │  │ FAISS + AI    │  │          │  │     │
│   │  │ QA pairs      │  │ responses     │  │ Google   │  │     │
│   │  │               │  │               │  │ Gemini   │  │     │
│   │  └──────┬────────┘  └───────────────┘  │ API      │  │     │
│   │         │                               └──────────┘  │     │
│   │         ▼                                             │     │
│   │  ┌──────────────────────────────────────────────┐    │     │
│   │  │           DATA LAYER                          │    │     │
│   │  │                                                │    │     │
│   │  │  embeddings/faiss_index.bin  → FAISS index     │    │     │
│   │  │  embeddings/meta.pkl        → Metadata         │    │     │
│   │  │  data/kcc_qa_pairs.json     → QA pairs source  │    │     │
│   │  └──────────────────────────────────────────────┘    │     │
│   └─────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User asks a question** (e.g., "How to control aphids in mustard?")
2. **FAISS Search**: The query is embedded using `all-MiniLM-L6-v2` sentence transformer and searched against the FAISS index
3. **Relevance Filtering**: Results with L2 distance > 1.3 are discarded (irrelevant)
4. **Confidence Scoring**: Each result gets a confidence score (0-100%)
5. **AI Enhancement** (Online Mode): If enabled, Gemini AI generates a comprehensive response using the FAISS results as context
6. **Fallback**: If no FAISS results match, Gemini provides a direct AI answer
7. **Response Displayed**: Results shown with confidence badges, source info, and metadata

---

## ✨ Features

### Core Features
| Feature | Description |
|---------|-------------|
| 🔍 **Semantic Search** | FAISS-powered search over 2,000+ KCC verified Q&A pairs |
| 🤖 **AI Enhancement** | Google Gemini generates comprehensive answers using retrieved context |
| 🌐 **Multi-language** | 8 Indian languages supported |
| 📊 **Confidence Scoring** | Every answer shows relevance percentage |
| 🔒 **Offline Mode** | Works without internet using local FAISS index |
| 🌿 **Crop Guide** | Comprehensive guide for crop management and cycles |
| 📈 **Price Prediction** | AI-powered 30-day price forecasts with state-specific data |
| 🇮🇳 **Farmer Advisory** | Buy/Sell/Hold guidance based on Agmarknet vs MSP 2025-26 |
| 📍 **Smart Location** | Auto-detected location with state-wise filtering (AP, MH, etc.) |

### Two User Interfaces
| Interface | Technology | URL | Best For |
|-----------|------------|-----|----------|
| **Streamlit UI** | Python + Streamlit | `localhost:8501` | Quick deployment, data science |
| **Dashboard** | HTML + Tailwind CSS + JS | `localhost:5000/dashboard/` | Modern web experience |

### Dashboard Highlights
- 🔐 **Secure Authentication** — Login/Register with session management
- 📍 **Live Market Prices** — Daily Agmarknet data from *data.gov.in*
- 📈 **State-Specific Forecasts** — Dedicated filters for **Andhra Pradesh**, Maharashtra, etc.
- 🇮� **Government MSP Sync** — Real-time comparison with **CCEA 2025-26** reference prices
- 🧠 **Honest AI Confidence** — Transparent "±~15% trend estimate" instead of misleading high percentages
- 🌤️ **Local Weather** — Auto-detected location based weather
- 💬 Real-time chat with typing indicators
- 🔥 Popular questions panel
- 🕐 Query history
- 🟢 Online/Offline AI toggle

> **See [API_GUIDE.md](API_GUIDE.md) for full details on external APIs used.**

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **AI Model** | Google Gemini, watsonx (`gemini-2.0-flash-001, watsonx`) | Natural language understanding & generation |
| **Vector Search** | FAISS (Facebook AI Similarity Search) | Fast semantic search over embeddings |
| **Embeddings** | `all-MiniLM-L6-v2` (Sentence Transformers) | Convert text to vector embeddings |
| **Backend API** | Flask + Flask-CORS | REST API for the dashboard |
| **Streamlit UI** | Streamlit 1.54+ | Alternative Python-based UI |
| **Dashboard UI** | HTML + Tailwind CSS + Vanilla JS | Modern responsive dashboard |
| **Dataset** | KCC (Kisan Call Centre) | Government-verified agricultural Q&A |
| **Language** | Python 3.9+ | Core language |

---

## 📁 Project Structure

```
krishiMind-ai/
│
├── app.py                          # 🐍 Streamlit UI
│                                   # Main entry point for the Python-based interface.
│                                   # Run with: streamlit run app.py
│
├── api_server.py                   # ⚡ Flask API Server
│                                   # REST API backend that powers the HTML dashboard.
│                                   # Handles routing, AI processing, and data serving.
│                                   # Run with: python api_server.py
│
├── dashboard/                      # 🎨 Modern Web Dashboard
│   ├── index.html                  # Main dashboard file. Built with HTML5 + Tailwind CSS.
│   ├── app.js                      # Frontend logic (Chart.js, API calls, dynamic UI).
│   └── styles.css                  # Custom styling and animations.
│
├── services/                       # ⚙️ Backend Micro-services
│   ├── faiss_store.py              # FAISS Service: Loads and searches the vector index.
│   ├── watsonx_service.py          # AI Service: Connects to Google Gemini API.
│   ├── query_handler.py            # Logic Core: Orchestrates offline search + online AI.
│   └── generate_embeddings.py      # Utility: Converts text to vectors using Sentence Transformers.
│
├── embeddings/                     # 🧠 Knowledge Base (Vector Store)
│   ├── faiss_index.bin             # The actual FAISS index file (binary).
│   ├── kcc_embeddings.pkl          # Serialized embeddings backup.
│   └── meta.pkl                    # Metadata mapping (Answer text, Crop, State) to index IDs.
│
├── data/                           # 📂 Raw Data
│   └── kcc_qa_pairs.json           # JSON dataset of 2,000+ verified agricultural Q&A pairs.
│
├── config.py                       # 🛠️ Configuration
│   # Central place for API keys, file paths, and model settings.
│
├── rebuild_index.py                # 🔄 Maintenance Script
│   # Run this to regenerate the FAISS index from the JSON dataset.
│
├── requirements.txt                # 📦 Dependencies
│   # List of all Python libraries (flask, streamlit, google-genai, faiss-cpu, etc.)
│
└── .env                            # 🔒 Secrets
    # Stores your API keys. (Never commit this file!)

```

---

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.9+** installed
- **Git** installed
- **Google Gemini API Key** (free at [aistudio.google.com](https://aistudio.google.com/apikey))

### Step 1: Clone the Repository

```bash
git clone https://github.com/satish024-024/KrishiMind-AI.git
cd KrishiMind-AI
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies:**
```
streamlit>=1.30.0
google-genai>=1.0.0
faiss-cpu>=1.7.4
sentence-transformers>=2.2.0
flask>=3.0.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
numpy>=1.24.0
```

### Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
```

**`.env` file contents:**
```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-2.0-flash-001

# Application Mode
OFFLINE_MODE=false
```

> **Get your API key free:** Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey), sign in with Google, and create an API key.

### Step 4: Verify Setup

```bash
python -c "from services.faiss_store import FAISSSearcher; s = FAISSSearcher(); s.load(); print(f'FAISS loaded: {s.index.ntotal} vectors')"
```

Expected output: `FAISS loaded: 2000 vectors`

---

## ▶️ Running the Application

### Option A: Streamlit UI (Traditional)

```bash
streamlit run app.py
```
Open: **http://localhost:8501**

### Option B: Modern Dashboard (Recommended)

```bash
python api_server.py
```
Open: **http://localhost:5000/dashboard/**

### Option C: Both simultaneously

```bash
# Terminal 1
streamlit run app.py

# Terminal 2
python api_server.py
```

---

## 📡 API Reference

The Flask API server (`api_server.py`) provides these endpoints:

### `GET /api/health`
Health check — returns service status.

**Response:**
```json
{
    "status": "ok",
    "faiss_ready": true,
    "ai_ready": true,
    "timestamp": "2026-02-16T19:45:00"
}
```

### `POST /api/query`
Process a farming question.

**Request:**
```json
{
    "query": "How to control aphids in mustard?",
    "online_mode": true,
    "top_k": 5
}
```

**Response:**
```json
{
    "query": "How to control aphids in mustard?",
    "offline_answer": "Based on KCC data...",
    "online_answer": "Here are effective methods to control aphids...",
    "results": [
        {
            "question": "What is the control measure of aphid in mustard?",
            "answer": "Spray neem oil 5ml/L every 10-15 days...",
            "confidence": 92,
            "distance": 0.104,
            "crop": "Mustard",
            "state": "Uttar Pradesh",
            "category": "Pest Management"
        }
    ],
    "num_results": 3,
    "elapsed": 1.25,
    "mode": "online"
}
```

### `GET /api/popular`
Get popular questions grouped by category.

**Response:**
```json
{
    "categories": [
        {
            "name": "Weather",
            "icon": "🌤️",
            "questions": ["Best time to sow paddy?", "..."]
        },
        {
            "name": "Pest Solutions",
            "icon": "🐛",
            "questions": ["How to control aphids?", "..."]
        }
    ]
}
```
### `GET /api/price-prediction`
Get 30-day price forecast and historical trends.
**Query Params:** `?crop=Wheat&state=Andhra Pradesh`
**Response:** Includes current price, predicted price, trend (rising/falling), confidence band, and methodology note.

### `GET /api/price-advisory`
Get actionable buy/sell/hold guidance for all major crops.
**Query Params:** `?state=Maharashtra` (optional)
**Response:** Actionable verdicts based on daily mandi prices vs govt. MSP 2025-26.

---

## 📈 AI Price Prediction & Advisory

The dashboard features a dedicated **Prediction & Advisory Engine** designed to help farmers make data-driven selling decisions.

### How Prediction Works
- **Model**: Weighted Moving Average (WMA-30) + Linear Regression Slope Analysis.
- **Accuracy**: Reported as an honest **±~15% trend estimate** (7-14 days most reliable).
- **Data Source**: Aggregated daily mandi prices from **Agmarknet (data.gov.in)**.
- **MSP Reference**: Latest **CCEA Govt. of India 2025-26** approved prices via *pib.gov.in*.

### Farmer Advisory Logic
The system generates three primary verdicts:
1. 🟢 **SELL NOW**: Market price is high and forecast is falling (Take profits!).
2. 🔴 **SELL AT MSP**: Market price is below MSP. Use government procurement for guaranteed income.
3. 🟡 **HOLD**: Market is stable or rising. Wait for better rates.

### Location Specificity
The engine supports **state-wise historical synchronization** for:
- **Andhra Pradesh** (Newly added!)
- Maharashtra, Punjab, Uttar Pradesh, Rajasthan, Madhya Pradesh, Gujarat, Haryana, Karnataka, West Bengal.

---

## 🧠 How It Works

### 1. Knowledge Base (FAISS)

The system uses a **FAISS (Facebook AI Similarity Search)** index built from 2,000 curated Q&A pairs from India's **Kisan Call Centre (KCC)** dataset.

```
Raw CSV (8GB) → Preprocessing → 2,000 QA pairs → Sentence Embeddings → FAISS Index
```

- **Embedding Model:** `all-MiniLM-L6-v2` (384-dimensional vectors)
- **Index Type:** L2 (Euclidean distance)
- **Max Distance Threshold:** 1.3 (results beyond this are filtered out)
- **Confidence Formula:** `confidence = max(0, 1 - distance / max_distance)`

### 2. AI Enhancement (Google Gemini)

When **Online Mode** is enabled:
- FAISS results are passed as context to Gemini
- Gemini generates a comprehensive, farmer-friendly answer
- System instruction guides Gemini as an "expert agricultural advisor for Indian farmers"

When **no FAISS results** match:
- Gemini receives the raw query directly
- Provides a general AI-powered response (handles greetings, general questions)

### 3. Query Processing Flow

```python
# Simplified flow
def process_query(query, online_mode=True, top_k=5):
    # 1. Search FAISS index
    results = faiss_searcher.search(query, top_k=top_k, max_distance=1.3)
    
    # 2. Build offline answer from top results
    offline_answer = format_results(results)
    
    # 3. If online mode, enhance with Gemini
    if online_mode and gemini_service:
        context = build_context(results)
        online_answer = gemini_service.generate_response(
            f"Based on this context: {context}\n\nAnswer: {query}"
        )
    
    return {
        'offline_answer': offline_answer,
        'online_answer': online_answer,
        'results': results
    }
```

---

## 📊 Dataset Information

### Source
- **Kisan Call Centre (KCC)** — Government of India's farmer helpline
- **Original Size:** ~8GB CSV with millions of records
- **Processed:** 2,000 high-quality Q&A pairs extracted and indexed

### Data Format (`data/kcc_qa_pairs.json`)
```json
[
    {
        "question": "What is the control measure of aphid in mustard?",
        "answer": "Spray neem oil solution (5ml/L) every 10-15 days...",
        "crop": "Mustard",
        "state": "Uttar Pradesh",
        "category": "Pest Management"
    }
]
```

### Rebuilding the Index

If you have the raw KCC CSV and want to rebuild:

```bash
python rebuild_index.py
```

This will:
1. Read the CSV
2. Extract Q&A pairs
3. Generate embeddings using `all-MiniLM-L6-v2`
4. Build and save the FAISS index

> **Note:** The pre-built FAISS index is included in the repo, so rebuilding is optional.

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `GEMINI_MODEL_NAME` | No | `gemini-2.0-flash-001` | Gemini model to use |
| `OFFLINE_MODE` | No | `false` | Set `true` to disable AI enhancement |

### Config File (`config.py`)

| Setting | Value | Description |
|---------|-------|-------------|
| `FAISS_INDEX_FILE` | `embeddings/faiss_index.bin` | Path to FAISS index |
| `METADATA_FILE` | `embeddings/meta.pkl` | Path to metadata |
| `SENTENCE_TRANSFORMER_MODEL` | `all-MiniLM-L6-v2` | Embedding model |
| `LLM_MAX_TOKENS` | `1024` | Max response length |
| `LLM_TEMPERATURE` | `0.7` | Response creativity (0-1) |

---

## 🌿 Branches

| Branch | Description |
|--------|-------------|
| `main` | Stable Streamlit-only version |
| `dashboard-ui` | Modern HTML/Tailwind dashboard + Flask API |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 👥 Team

**KrishiMind AI** is developed as part of an agricultural technology initiative to empower Indian farmers with AI-powered insights.

---

## 📄 License

This project is for educational and hackathon purposes.

---

## 🆘 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `FAISS index not found` | Run `python rebuild_index.py` or check `embeddings/` folder |
| `API key error` | Verify `GEMINI_API_KEY` in `.env` file |
| `Module not found` | Run `pip install -r requirements.txt` |
| `Port already in use` | Kill existing process or use a different port |
| `No relevant results` | Try different phrasing or check FAISS index is loaded |

### Quick Test

```bash
# Test FAISS search
python test_relevance.py

# Test API
curl http://localhost:5000/api/health

# Test query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How to control aphids?", "online_mode": true}'
```

---

**Made with ❤️ for Indian Farmers 🇮🇳**
