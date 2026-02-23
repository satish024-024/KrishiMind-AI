# 🌾 Agri Advisor — Smart Agriculture Assistant

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
- [Enhanced Features](#-enhanced-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Running the Application](#-running-the-application)
- [API Reference](#-api-reference)
- [AI Price Prediction & Advisory](#-ai-price-prediction--advisory)
- [How It Works](#-how-it-works)
- [Dataset Information](#-dataset-information)
- [Contributing](#-contributing)
- [Team](#-team)

---

## 🌟 Overview

**Agri Advisor** is an intelligent agricultural assistant designed specifically for Indian farmers. It combines:

1. **FAISS Semantic Search** — Searches through 2,000+ verified Q&A pairs from India's Kisan Call Centre (KCC) dataset to find the most relevant answers.
2. **Google Gemini AI** — Enhances results with AI-generated explanations and handles general queries that aren't in the knowledge base.
3. **Multi-language Support** — Supports English, Hindi (हिन्दी), Marathi (मराठी), Telugu (తెలుగు), Tamil (தமிழ்), Kannada (ಕನ್ನಡ), Bengali (বাংলা), and Gujarati (ગુજરાતી).

### Problem Statement

Indian farmers often lack access to timely, accurate agricultural information. Agri Advisor solves this by providing:
- Instant answers to farming questions via a RAG-based AI system.
- AI-powered crop and pest advice derived from verified government (KCC) data.
- Transparency through confidence scoring.
- Advanced market insights to optimize selling decisions.

---

## 🏗 Architecture

Agri Advisor follows a robust **Retrieval-Augmented Generation (RAG)** architecture:

1. **User Query**: Farmer asks a question in their native language.
2. **Semantic Retrieval**: The query is embedded using `all-MiniLM-L6-v2` and searched against a FAISS vector index.
3. **Context Injection**: Relevant verified facts are retrieved and injected into the AI prompt.
4. **AI Synthesis**: Google Gemini generates a natural, helpful response grounded in the retrieved facts.
5. **Hybrid Mode**: If offline, the system serves direct facts from the knowledge base.

---

## ✨ Enhanced Features

### 🚀 Core Intelligent Services
| Feature | Description |
|---------|-------------|
| 🔍 **Semantic Search** | FAISS-powered search over 2,000+ KCC verified Q&A pairs. |
| 🤖 **AI Enhancement** | Google Gemini generates comprehensive answers using retrieved context. |
| 🌐 **Multi-language** | Support for 8 Indian languages with seamless switching. |
| 📈 **Price Prediction** | 30-day price forecasts using Weighted Moving Average (WMA-30). |
| ⚖️ **Market Advisory** | Actionable "Buy/Sell/Hold" verdicts based on Agmarknet vs MSP 2025-26. |

### 🛠 Advanced Market Tools (New)
| Tool | Description |
|------|-------------|
| 🕙 **Sell Timing Optimizer** | Analyzes daily trends to suggest the absolute best window to sell crops. |
| 🔁 **Crop Alternatives** | Suggests alternative crops based on price trends and soil suitability. |
| 📊 **Inter-State Comparison** | Compares mandi prices across different states for better arbitrage. |
| 📍 **Smart Location** | Auto-detected location with state-wise price filtering (AP, MH, etc.). |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| **AI Model** | Google Gemini (`gemini-2.0-flash-001`) |
| **Vector Search** | FAISS (Facebook AI Similarity Search) |
| **Embeddings** | `all-MiniLM-L6-v2` (Sentence Transformers) |
| **Backend API** | Flask + Flask-CORS + Python 3.9+ |
| **Dashboard UI** | HTML5 + Tailwind CSS + Vanilla JS + Chart.js |
| **Data Source** | KCC (Kisan Call Centre), Agmarknet (data.gov.in) |

---

## 📁 Project Structure

```
agri-advisor/
├── api_server.py           # ⚡ REST API backend powering the dashboard
├── app.py                  # 🐍 Streamlit alternate UI
├── dashboard/              # 🎨 Modern Web Dashboard files
│   ├── index.html          # Main entry point (Login/Register redirected)
│   ├── mobile.html         # Mobile-specific optimized UI
│   ├── app.js              # Frontend logic and API integration
│   └── styles.css          # Custom animations and styling
├── services/               # ⚙️ Micro-services
│   ├── faiss_store.py      # Vector search operations
│   ├── watsonx_service.py  # Gemini AI service wrapper
│   ├── price_predictor.py  # Market analysis and forecasting logic
│   └── query_handler.py    # Orchestration of RAG pipeline
├── embeddings/             # 🧠 Knowledge Base (Vector Index)
├── data/                   # 📂 Raw KCC Q&A dataset
└── requirements.txt        # 📦 Project dependencies
```

---

## 🚀 Setup & Installation

1. **Clone & Install**:
   ```bash
   git clone https://github.com/satish024-024/Agri-Advisor.git
   cd Agri-Advisor
   pip install -r requirements.txt
   ```

2. **Configure Environments**: Create a `.env` file from `.env.example` and add your `GEMINI_API_KEY`.

3. **Run the Server**:
   ```bash
   python api_server.py
   ```
   Open **http://localhost:5000/dashboard/** to access the dashboard.

---

## 📡 API Reference (Key Endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/query` | Process a farming question (RAG-based). |
| `GET` | `/api/price-prediction` | Fetch 30-day forecasts for specific crops. |
| `GET` | `/api/price-advisory` | Get Buy/Sell/Hold verdicts vs MSP 2025-26. |
| `GET` | `/api/sell-timing` | Optimal sell window analysis. |
| `GET` | `/api/crop-alternatives` | Compare and suggest alternative crops. |
| `GET` | `/api/state-comparison` | Cross-state mandi price analytics. |

---

## 📈 AI Price Prediction & Advisory

The dashboard features a dedicated **Prediction Engine** designed to help farmers make data-driven selling decisions:
- **Model**: Trend analysis using historical data from Agmarknet.
- **Accuracy**: Transparently reported as a trend estimate (±15%).
- **Reference**: Compared against **CCEA 2025-26** MSP prices.
- **Verdicts**: 🟢 SELL NOW, 🔴 SELL AT MSP, 🟡 HOLD.

---

## 🤝 Team

**Agri Advisor** is a mission-driven project aimed at empowering 140 million Indian farming households through the power of Generative AI.

---
**Made with ❤️ for Indian Farmers 🇮🇳**
