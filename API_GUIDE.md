# 🔑 KrishiMind AI — API Setup Guide

## All APIs Used in This Project

This document lists every external API and data source used by KrishiMind AI, how to get access, and what each provides.

---

## 1. 🌤️ Weather — Open-Meteo API
> **Status: ✅ Already working — FREE, No API key needed!**

| Property | Value |
|----------|-------|
| Base URL | `https://api.open-meteo.com/v1/forecast` |
| Auth | None required |
| Cost | Free (open-source) |
| Rate limit | 10,000 requests/day |
| Data | Temperature, humidity, wind, weather code, soil moisture, 7-day forecast |

### What it provides to KrishiMind:
- Current temperature, humidity, wind speed
- 7-day forecast (max/min temps, precipitation)
- Soil moisture data (for the gauge widget)
- Weather code for icons (clear, rain, storm, etc.)

### No setup needed — just works!

---

## 2. 🤖 AI Service — Google Gemini API
> **Status: ✅ Already configured**

| Property | Value |
|----------|-------|
| Console | [Google AI Studio](https://aistudio.google.com) |
| Auth | API Key |
| Cost | Free tier: 60 requests/minute |
| Model | `gemini-3-flash-preview` |

### How to get the API key:
1. Go to → **https://aistudio.google.com/apikey**
2. Click **"Create API Key"**
3. Copy the API key
4. Create `.env` file in project root:
   ```
   GOOGLE_API_KEY=your_key_here
   ```
5. Or set it as environment variable:
   ```bash
   export GOOGLE_API_KEY=your_key_here     # Linux/Mac
   set GOOGLE_API_KEY=your_key_here        # Windows CMD
   $env:GOOGLE_API_KEY="your_key_here"     # Windows PowerShell
   ```

### Free tier limits:
- 60 requests per minute
- 1,500 requests per day 
- Generous enough for demo/hackathon use

---

## 3. 💰 Market Prices — Government of India MSP Data
> **Status: ✅ Using real government MSP rates (hardcoded from gazette)**

### Current Implementation:
We use **official MSP (Minimum Support Price) rates for 2024-25** published by the Ministry of Agriculture & Farmers Welfare, Government of India.

### To get LIVE mandi prices (optional upgrade):

#### Option A: data.gov.in API (Recommended)
| Property | Value |
|----------|-------|
| Portal | [data.gov.in](https://data.gov.in) |
| Dataset | "Current Daily Price of Various Commodities from Various Markets" |
| Auth | API Key (free registration) |
| Cost | FREE |

**Steps to get API key:**
1. Go to → **https://data.gov.in**
2. Click **"Register"** → Create an account (use any email)
3. After login → Go to **"APIs"** tab
4. Search for: **"Daily Price of Various Commodities"**
5. Click on the dataset → Click **"Generate API Key"**
6. Copy the API key
7. The endpoint format is:
   ```
   https://api.data.gov.in/resource/<resource_id>?api-key=<YOUR_KEY>&format=json&filters[commodity]=Wheat
   ```

#### Option B: CEDA API (Ashoka University)
| Property | Value |
|----------|-------|
| Portal | [CEDA Data Portal](https://ceda.ashoka.edu.in) |
| Auth | API Key (free for non-commercial) |
| Cost | FREE for academic/non-commercial |

**Steps:**
1. Go to → **https://ceda.ashoka.edu.in**
2. Register for free (click Sign Up)
3. After login → Navigate to **"API Access"**
4. Generate your API key
5. Docs: https://ceda.ashoka.edu.in/api/agmarknet/docs

---

## 4. 🌍 Soil Data — SoilGrids API (Optional Enhancement)
> **Status: 🔄 Not yet integrated (soil moisture comes from Open-Meteo)**

| Property | Value |
|----------|-------|
| Portal | [SoilGrids](https://rest.isric.org) |
| Auth | None required |
| Cost | FREE |
| Data | Soil type, organic carbon, pH, clay/silt/sand content |

### To integrate:
```
GET https://rest.isric.org/soilgrids/v2.0/properties/query?lon=77.75&lat=20.93&property=phh2o&property=soc&depth=0-5cm
```

This gives detailed soil composition data for any GPS coordinate.

---

## 5. 🌾 Crop & Pest Knowledge Base — FAISS + Kisan Call Centre
> **Status: ✅ Already loaded from CSV dataset**

This is NOT an external API. It's a local FAISS vector index built from the **Kisan Call Centre** dataset (30,000+ farmer Q&A pairs) provided by the Government of India.

### Dataset source:
- **Kisan Call Centre Records** from Ministry of Agriculture
- Available at: [data.gov.in](https://data.gov.in/search?title=kisan+call+centre)
- Also: [Kaggle India Agriculture Dataset](https://www.kaggle.com/datasets)

### How it works:
1. CSV data is loaded into FAISS vector index
2. User queries are matched against 30K+ Q&A pairs
3. Top matching answers are sent to Gemini as context
4. Gemini generates a refined, location-aware answer

---

## 6. 📰 News & Govt Schemes — Optional Future APIs

### Agriculture News API
| Property | Value |
|----------|-------|
| Portal | [NewsAPI.org](https://newsapi.org) |
| Auth | API Key |
| Cost | Free for development |

**Steps:**
1. Go to → **https://newsapi.org/register**
2. Register with email
3. Get API key instantly
4. Query: `https://newsapi.org/v2/everything?q=agriculture+india&apiKey=YOUR_KEY`

### PM-KISAN / Govt Scheme Data
| Property | Value |
|----------|-------|
| Portal | [api.data.gov.in](https://api.data.gov.in) |
| Description | Government scheme data including PM-KISAN beneficiary data |

---

## 7. 🗺️ Geocoding / Reverse Geocoding — Optional
> For auto-detecting user's city from GPS coordinates

| Property | Value |
|----------|-------|
| API | [Nominatim (OpenStreetMap)](https://nominatim.org) |
| Auth | None (just set User-Agent header) |
| Cost | FREE |
| Limit | 1 request/second |

```
GET https://nominatim.openstreetmap.org/reverse?lat=20.93&lon=77.75&format=json
→ Returns: "Amravati, Maharashtra, India"
```

Could be used to auto-detect location from browser GPS.

---

## Quick Summary Table

| API | Purpose | Key Needed? | Cost | Status |
|-----|---------|-------------|------|--------|
| Open-Meteo | Weather, soil moisture | ❌ None | Free | ✅ Working |
| Google Gemini | AI responses | ✅ API Key | Free tier | ✅ Working |
| Govt. MSP Data | Market prices | ❌ Hardcoded | Free | ✅ Working |
| data.gov.in | Live mandi prices | ✅ API Key | Free | 🔄 Optional |
| CEDA (Ashoka) | Historical mandi data | ✅ API Key | Free | 🔄 Optional |
| SoilGrids | Detailed soil data | ❌ None | Free | 🔄 Optional |
| NewsAPI | Agriculture news | ✅ API Key | Free | 🔄 Future |
| Nominatim | Location auto-detect | ❌ None | Free | 🔄 Future |
| FAISS Index | Kisan Call Centre KB | ❌ Local | Free | ✅ Working |

---

## 🚀 Priority Upgrade Path

If you want to add more real-time data, do these in order:

1. **data.gov.in** → Live daily mandi prices (biggest impact)
2. **SoilGrids** → Detailed soil report for user's location
3. **Nominatim** → Auto-detect location from GPS
4. **NewsAPI** → Show agriculture news feed on dashboard

All of these are **FREE** and take ~5 minutes to set up each!
