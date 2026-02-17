# KrishiMind AI - Deployment Guide

This project consists of two parts:
1. **Frontend**: HTML/CSS/JS Dashboard (`dashboard/` folder)
2. **Backend**: Python Flask API (`api_server.py`) or Streamlit App (`app.py`)

Since the backend includes **AI/ML libraries** (PyTorch, FAISS) which are >500MB, it **cannot** be deployed on Vercel's standard plan (Serverless functions have a 250MB limit).

Here is the **recommended deployment strategy**:

---

## 🚀 Option 1: Streamlit Cloud (Easiest & Free)
Best for deploying the `app.py` version.
1. Push code to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Deploy `app.py`.
4. Add secrets (API Keys) in the dashboard settings.

---

## ⚡ Option 2: Render (Recommended for Custom Dashboard)
Best for the Flask Backend + Custom HTML Dashboard.
1. Push code to GitHub.
2. Go to [render.com](https://render.com/).
3. Create a **Web Service**.
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `gunicorn api_server:app`
6. **Environment Variables**: Add `GEMINI_API_KEY`.

---

## ▲ Option 3: Vercel (Frontend Only)
You can host the **HTML Dashboard** on Vercel, but you **MUST** host the backend elsewhere (like Render) because Vercel cannot handle the heavy AI models.

### Step 1: Deploy Backend on Render
Follow "Option 2" above to deploy your Flask API on Render.
Get your Render URL (e.g., `https://krishi-mitra-api.onrender.com`).

### Step 2: Configure Frontend for Vercel
1. Create a `vercel.json` in the root (optional, for rewrites).
2. Edit `dashboard/index.html` to point to your Render Backend.
   Add this script tag inside the `<head>` **before** `app.js` is loaded:
   ```html
   <script>
       // Point this to your Render Backend URL
       window.KRISHI_API_URL = "https://YOUR-RENDER-APP-NAME.onrender.com/api";
   </script>
   ```

### Step 3: Deploy to Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel`.
3. Set the **Root Directory** to `dashboard` (IMPORTANT!).
4. Deploy!

Now your fast Vercel frontend talks to your powerful Render backend.
