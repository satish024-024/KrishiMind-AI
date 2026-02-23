# 🌾 Agri Advisor - Hackathon Presentation

---

## Slide 1: Title
### **Agri Advisor: Empowering Farmers with Generative AI**
**Subtitle:** Intelligent Agricultural Query Resolution & Price Advisory System

**Team:** [Team Name]
**Focus:** Accessibility, Precision, and Data-Driven Farming.

---

## Slide 2: Problem Statement 🛡️
### **The Knowledge Gap in Indian Agriculture**
*   **Information Asymmetry:** Farmers lack instant access to verified, expert agricultural advice.
*   **Price Volatility:** High fluctuations in mandi prices lead to poor selling decisions.
*   **Language Barrier:** Most digital tools are not accessible in regional Indian languages.
*   **Low Connectivity:** Rural areas often face unstable internet, making online-only solutions unreliable.

---

## Slide 3: The Solution 💡
### **A Unified Intelligent Dashboard**
*   **AI-Powered Q&A:** Instant answers derived from 2,000+ verified Kisan Call Centre (KCC) pairs.
*   **Price Prediction & Advisory:** Data-driven "Buy/Sell/Hold" guidance based on real-time Agmarknet trends.
*   **Omni-Channel UI:** A modern, mobile-optimized Bento-grid dashboard and a lightweight Streamlit interface.
*   **Multilingual Support:** Accessible in 8+ major Indian languages (Hindi, Telugu, Marathi, etc.).

---

## Slide 4: Methodology & Architecture 🏗️
### **Retrieval-Augmented Generation (RAG)**
*   **Semantic Search:** FAISS (Facebook AI Similarity Search) used for sub-second retrieval from vector databases.
*   **Vector Embeddings:** Queries processed using `all-MiniLM-L6-v2` for deep semantic understanding.
*   **Hybrid AI Logic:**
    1.  **Offline Mode:** Fetches verified facts from local knowledge base (Reliability).
    2.  **Online Mode:** Google Gemini synthesizes answers for nuanced queries (Intelligence).
*   **Data Pipeline:** Automated cleaning and metadata enrichment of KCC government datasets.

---

## Slide 5: Technical Stack 🛠️
### **Modern, Scalable & Open-Source**
*   **AI/LLM:** Google Gemini (Generative AI), Sentence Transformers (Embeddings).
*   **Vector Engine:** FAISS (High-performance vector similarity search).
*   **Backend:** Flask (REST API), Python 3.9+.
*   **Frontend:** HTML5, Tailwind CSS, Vanilla JS, Chart.js (Data Visualization).
*   **APIs:** data.gov.in (Real-time Mandi Prices), Open-Meteo (Live Weather).
*   **Deployment:** Vercel/Railway ready configuration.

---

## Slide 6: Innovation & Novelty 🚀
### **Beyond a Basic Chatbot**
*   **Hybrid Offline-First AI:** Works without internet by falling back to local FAISS index—critical for rural India.
*   **Honest Confidence Scoring:** Transparently displays a ±15% trend estimate instead of absolute "true" predictions.
*   **Bento-Grid Dashboard:** High data-density UI showing Weather, Market, and AI Advice at a glance.
*   **State-Specific Synchronization:** Context-aware responses based on local mandi rates (e.g., specific logic for AP, MH).

---

## Slide 7: UI/UX & User Experience 🎨
### **Designed for Ease of Use**
*   **Mobile-Responsive:** Tailored experience for low-end smartphones common in rural areas.
*   **Visual Data:** Complex price trends simplified into intuitive graphs and color-coded "Verdicts" (SELL/HOLD).
*   **Accessibility:** Real-time chat with typing indicators and popular question shortcuts for low-literacy users.
*   **Dynamic Design:** Vibrant, modern aesthetics using Tailwind CSS to provide a premium user experience.

---

## Slide 8: Impact & Feasibility 📈
### **Scaling Agricultural Success**
*   **Social Impact:** Empowers farmers with expert knowledge, reducing dependency on middlemen.
*   **Economic Benefit:** Data-driven selling guidance ensures farmers sell at peak prices, increasing overall income.
*   **Feasibility:** Built using 100% open-source libraries and public government data APIs.
*   **Scalability:** Modular architecture allows adding image-based disease detection and voice-input features easily.

---

## Slide 9: Research, References & Thanks 🙏
### **Sources of Truth**
*   **KCC (Kisan Call Centre):** 2,000+ verified government horticultural & agricultural Q&A pairs.
*   **Agmarknet (data.gov.in):** Real-time daily market price feeds.
*   **CCEA pib.gov.in:** 2025-26 reference MSP (Minimum Support Prices).
*   **Special Thanks:** To our mentors and the jury for this opportunity.

**Agri Advisor — Empowering the Hands that Feed Us.**
