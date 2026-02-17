# KrishiMind AI Presentation Script

## 1. SATISH KUMAR - Team Lead
**(Introduction + Problem Statement - 2 Minutes)**

"Good morning respected judges and mentors.

We are Team [Your Team Name], presenting our solution titled **KrishiMind AI – Generative AI Powered Agricultural Query Resolution System**.

Agriculture is the backbone of India's economy. However, farmers in rural areas often lack immediate access to expert guidance on crop diseases, pest control, fertilizers, and government schemes.

Existing helplines like Kisan Call Centres provide support, but scalability, instant accessibility, and visual data representation remain major challenges.

To bridge this knowledge gap, we have moved beyond basic chatbots. We designed a comprehensive, **AI-powered Intelligent Agricultural Dashboard**. Unlike standard interfaces, our system aggregates real-time data and AI advice into a single, high-performance web platform that works seamlessly even in low-connectivity zones.

Our system works in two synchronized modes:
*   **Offline Retrieval Mode**: Using FAISS for instant access to verified government data.
*   **Online Generative Mode**: Using IBM Watsonx Granite LLM for complex reasoning.

Our objective is to ensure Accessibility, Reliability, and Data-Driven Decision Making for every farmer."

---

## 2. PHANI - AI & RAG Architecture
**(Core Technical Architecture - 2-3 Minutes)**

"Our system follows a robust **Retrieval-Augmented Generation (RAG) Architecture**.

Instead of directly generating answers, which can lead to hallucinations, we first retrieve relevant verified agricultural knowledge using semantic vector search.

**Architecture Flow:**
1.  **User Query Contextualization**: We capture not just the text, but the user's location, current season (Rabi/Kharif), and language.
2.  **Query Embedding**: We use the 'all-MiniLM-L6-v2' Sentence Transformer to convert the query into a vector.
3.  **Similarity Search**: We utilize **FAISS (Facebook AI Similarity Search)** to find the top-k relevant entries from our knowledge base.
4.  **Hybrid Output Generation**:
    *   If offline, we serve the direct retrieved answer.
    *   If online, we construct a structured prompt injecting the retrieved context and send it to the **IBM Watsonx Granite LLM**.

This ensures our responses are always grounded in real agricultural data."

---

## 3. GOWRI - Data Processing & Embeddings
**(Data & Vector Intelligence - 2 Minutes)**

"The intelligence of our system is built on verified data sourced from Kisan Call Centre records and Government Agricultural Data.

**Step 1: Data Preprocessing**
*   We cleaned raw datasets, removed duplicates, and standardized the Question-Answer format.
*   We enriched this data with metadata like Crop Type, State, and Season.

**Step 2: Embedding Generation**
*   Using the Sentence Transformer model, we converted thousands of agricultural Q&A pairs into dense vector representations.
*   These are stored in a serialized format, allowing the system to understand semantic meaning.

For example, the system understands that 'Whitefly treatment' and 'controlling sucking pests in cotton' are semantically similar, retrieving the correct remedy even if the keywords don't match exactly."

---

## 4. VIJAY - Granite LLM Integration
**(Online Mode - 2 Minutes)**

"To enhance contextual understanding and conversational fluency, we integrated the **IBM Watsonx Granite LLM** (ibm/granite-3-8b-instruct).

While retrieval gives us facts, the LLM gives us **explanation and synthesis**.

**How it works:**
1.  FAISS retrieves the top 5 relevant facts.
2.  We construct a dynamic prompt that includes the farmer's location (e.g., 'Amravati') and the current live weather context.
3.  The Granite LLM generates a refined, natural language response in the farmer's preferred language (English, Hindi, Telugu, etc.).

This dual architecture ensures that even if the internet fails, the system automatically falls back to the FAISS offline mode, ensuring reliability in rural environments."

---

## 5. JAGADEESH - User Interface & Impact
**(UI Data Visualization - 2 Minutes)**

"We have completely transformed the user experience. We moved away from simple chat interfaces to a **Modern, Responsive Web Dashboard** built with HTML5, CSS3, and Vanilla JavaScript.

**Key Dashboard Features:**
1.  **Bento Grid Layout**: A highly visual, data-dense layout that shows Weather, Soil Health, and Market Prices at a glance.
2.  **Real-Time Widgets**:
    *   **Live Weather**: Integrated with Open-Meteo API for 7-day forecasts and soil moisture tracking.
    *   **Market Ticker**: Real-time mandi prices sourced from data.gov.in APIs.
    *   **Crop Calendar**: An interactive timeline that automatically updates based on the current season (Rabi/Kharif).
3.  **Advanced Alert System**: Visual indicators for 'Offline Mode' and internet connectivity status.

**Impact:**
Our solution empowers farmers with instant decision-making tools. It reduces dependency on physical visits to help centers and provides a 24/7 digital assistant that is accessible via any mobile browser or kiosk.

**Future Scope:**
*   Voice-to-Text inputs for accessibility.
*   Image-based plant disease detection.
*   Direct integration with e-NAM for selling produce.

**Closing:**
In conclusion, KrishiMind AI demonstrates how Generative AI combined with a modern, data-rich user interface can transform agricultural advisory systems in India. Thank you."
