"""
KrishiMind AI — REST API Server
Wraps existing FAISS + Gemini services for the new dashboard
"""

import sys
import os
import time
import json
import traceback
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS

from config import FAISS_INDEX_FILE, METADATA_FILE, GEMINI_API_KEY
from services.faiss_store import FAISSSearcher
from services.query_handler import QueryHandler
from services import auth_service

DASHBOARD_DIR = Path(__file__).parent / 'dashboard'

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # Secure session key
CORS(app)

# ── Global service instances ─────────────────────────────
faiss_searcher = None
watsonx_service = None


def get_faiss_searcher():
    global faiss_searcher
    if faiss_searcher is None:
        try:
            faiss_searcher = FAISSSearcher()
            faiss_searcher.load()
            print("[OK] FAISS searcher loaded")
        except Exception as e:
            print(f"[WARN] FAISS load failed: {e}")
    return faiss_searcher


def get_watsonx_service():
    global watsonx_service
    if watsonx_service is None and GEMINI_API_KEY:
        try:
            from services.watsonx_service import WatsonxService
            watsonx_service = WatsonxService()
            watsonx_service.initialize()
            print("[OK] AI service loaded (Gemini)")
        except Exception as e:
            print(f"[WARN] AI service failed: {e}")
    return watsonx_service


# ── AUTHENTICATION ROUTES ────────────────────────────────

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect('/dashboard')
    return send_from_directory(str(DASHBOARD_DIR), 'login.html')

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    user = auth_service.login_user(data.get('username'), data.get('password'))
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        return jsonify({'success': True, 'user': user})
    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Missing fields'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'success': False, 'message': 'Password too short (min 6 chars)'}), 400

    success = auth_service.register_user(data['username'], data['password'], data.get('full_name', 'Farmer'))
    if success:
        # Auto login after register
        user = auth_service.login_user(data['username'], data['password'])
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        return jsonify({'success': True, 'message': 'Registered successfully'})
    return jsonify({'success': False, 'message': 'Username already taken'}), 409

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/me', methods=['GET'])
def api_me():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'username': session.get('username'),
            'full_name': session.get('full_name')
        })
    return jsonify({'authenticated': False}), 401


# ── Serve Dashboard (Protected) ──────────────────────────

@app.route('/dashboard/')
@app.route('/dashboard')
@app.route('/')
def serve_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return send_from_directory(str(DASHBOARD_DIR), 'index.html')

@app.route('/dashboard/<path:filename>')
def serve_dashboard_files(filename):
    # Allow public access to css/js/images even if not logged in (needed for login page styles)
    if filename in ['login.html', 'styles.css', 'app.js']:
        return send_from_directory(str(DASHBOARD_DIR), filename)
    
    if 'user_id' not in session and not filename.endswith(('.css', '.js', '.png', '.jpg', '.svg', '.ico')):
        return redirect('/login')
        
    return send_from_directory(str(DASHBOARD_DIR), filename)


# ── API Routes ───────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'auth_enabled': True,
        'faiss_ready': get_faiss_searcher() is not None,
        'ai_ready': get_watsonx_service() is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json()
    if not data or not data.get('query'):
        return jsonify({'error': 'Missing query'}), 400

    user_query = data['query'].strip()[:500]
    online_mode = data.get('online_mode', True)
    top_k = min(data.get('top_k', 5), 10)
    location = data.get('location', 'India')  # e.g. "Lucknow, UP"
    language = data.get('language', 'en')

    start = time.time()

    # Build date/season context
    now = datetime.now()
    month = now.month
    if month >= 10 or month <= 3:
        season = 'Rabi'
        season_crops = 'Wheat, Mustard, Barley, Chickpea, Peas'
    elif 6 <= month <= 9:
        season = 'Kharif'
        season_crops = 'Rice, Maize, Cotton, Soybean, Groundnut'
    else:
        season = 'Zaid'
        season_crops = 'Watermelon, Cucumber, Moong, Sunflower'

    context_info = (
        f"Current Date: {now.strftime('%d %B %Y, %A')}\n"
        f"Current Time: {now.strftime('%I:%M %p IST')}\n"
        f"Location: {location}\n"
        f"Season: {season} (main crops: {season_crops})\n"
        f"Month: {now.strftime('%B')}\n"
    )

    searcher = get_faiss_searcher()
    if not searcher:
        return jsonify({'error': 'Knowledge base not loaded'}), 503

    ai = get_watsonx_service() if online_mode else None
    handler = QueryHandler(searcher, ai)

    try:
        result = handler.process_query(
            user_query, top_k=top_k,
            online_mode=online_mode and ai is not None,
            location_context=context_info,
            language=language
        )
        elapsed = time.time() - start

        retrieved = []
        for r in result.get('retrieved_results', []):
            retrieved.append({
                'question': r['metadata'].get('question', ''),
                'answer': r['metadata'].get('answer', ''),
                'confidence': round(r.get('confidence', 0) * 100),
                'distance': round(r.get('distance', 0), 3),
                'crop': r['metadata'].get('crop', ''),
                'state': r['metadata'].get('state', ''),
                'category': r['metadata'].get('category', ''),
            })

        ai_answer = result.get('online_answer', '')
        if not retrieved and ai and online_mode:
            try:
                LANG_MAP = {
                    'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi', 'te': 'Telugu',
                    'ta': 'Tamil', 'kn': 'Kannada', 'bn': 'Bengali', 'gu': 'Gujarati',
                    'ml': 'Malayalam', 'pa': 'Punjabi'
                }
                lang_name = LANG_MAP.get(language, language)
                lang_instr = ""
                if language != 'en':
                    lang_instr = f"\nIMPORTANT: Answer strictly in {lang_name} language."
                
                prompt = (
                    f"Context:\n{context_info}\n"
                    f"A farmer in {location} asked: '{user_query}'.\n"
                    f"Provide a helpful, practical response specific to their "
                    f"location and the current {season} season in India.\n"
                    f"{lang_instr}"
                )
                ai_answer = ai.generate_response(prompt)
            except:
                pass

        return jsonify({
            'query': user_query,
            'offline_answer': result.get('offline_answer', ''),
            'online_answer': ai_answer or '',
            'results': retrieved,
            'num_results': len(retrieved),
            'elapsed': round(elapsed, 2),
            'mode': 'online' if (online_mode and ai) else 'offline',
            'location': location,
            'timestamp': now.strftime('%d %b %Y, %I:%M %p')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500




# ── LIVE MARKET PRICES from data.gov.in ──────────────────
DATAGOV_API_KEY = '579b464db66ec23bdd0000014d9fdfa6dbf34dfc731474736312f8b6'
DATAGOV_RESOURCE = '35985678-0d79-46b4-9ed6-6f13308a1d24'
_market_cache = {'data': None, 'ts': 0}  # Cache for 30 minutes

# MSP rates 2025-26 — CCEA approved (PIB: pib.gov.in | agriwelfare.gov.in)
MSP_DATA = {
    'Wheat':    {'msp': 2425, 'icon': '🌾', 'msp_year': '2025-26'},
    'Rice':     {'msp': 2369, 'icon': '🍚', 'msp_year': '2025-26'},  # Paddy Common
    'Mustard':  {'msp': 5950, 'icon': '🌻', 'msp_year': '2025-26'},
    'Cotton':   {'msp': 7710, 'icon': '🏵️', 'msp_year': '2025-26'},  # Medium Staple
    'Soyabean': {'msp': 5328, 'icon': '🫘', 'msp_year': '2025-26'},
    'Maize':    {'msp': 2400, 'icon': '🌽', 'msp_year': '2025-26'},
    'Gram':     {'msp': 5650, 'icon': '🫘', 'msp_year': '2025-26'},
    'Onion':    {'msp': None, 'icon': '🧅', 'msp_year': None},
    'Tomato':   {'msp': None, 'icon': '🍅', 'msp_year': None},
    'Potato':   {'msp': None, 'icon': '🥔', 'msp_year': None},
}

COMMODITIES_TO_FETCH = ['Wheat', 'Rice', 'Tomato', 'Onion', 'Cotton', 'Soyabean', 'Maize', 'Gram', 'Potato', 'Mustard']

def _fetch_live_prices(state=None):
    """Fetch mandi prices from data.gov.in.
    Filters by state when provided. data.gov.in updates daily (not real-time).
    """
    import urllib.request, urllib.parse
    PRICE_BOUNDS = {
        'Wheat': (1500, 4000), 'Rice': (1800, 5000), 'Tomato': (200, 8000),
        'Onion': (300, 6000), 'Cotton': (5000, 12000), 'Soyabean': (3500, 7000),
        'Maize': (1000, 3500), 'Gram': (3500, 8000), 'Potato': (300, 4000),
        'Mustard': (4000, 9000),
    }
    results = []
    for commodity in COMMODITIES_TO_FETCH:
        try:
            filters = {
                'api-key': DATAGOV_API_KEY,
                'format': 'json',
                'limit': 20,
                'filters[Commodity]': commodity,
                'sort[Arrival_Date]': 'desc'
            }
            if state:
                filters['filters[State]'] = state

            params = urllib.parse.urlencode(filters)
            url = f'https://api.data.gov.in/resource/{DATAGOV_RESOURCE}?{params}'
            req = urllib.request.Request(url, headers={'User-Agent': 'KrishiMindAI/1.0'})
            r = urllib.request.urlopen(req, timeout=10)
            data = json.loads(r.read())

            records = data.get('records', [])

            # If state-filtered returned nothing, fall back to national
            if not records and state:
                filters.pop('filters[State]', None)
                filters['limit'] = 20
                params = urllib.parse.urlencode(filters)
                url = f'https://api.data.gov.in/resource/{DATAGOV_RESOURCE}?{params}'
                req = urllib.request.Request(url, headers={'User-Agent': 'KrishiMindAI/1.0'})
                r = urllib.request.urlopen(req, timeout=10)
                data = json.loads(r.read())
                records = data.get('records', [])
                state_used = 'India (national fallback)'
            else:
                state_used = state or 'India'

            if not records:
                continue

            # Filter prices to sane bounds
            lo, hi = PRICE_BOUNDS.get(commodity, (100, 100000))
            valid_modals = [int(rec['Modal_Price']) for rec in records
                           if rec.get('Modal_Price') and lo <= int(float(rec['Modal_Price'])) <= hi]
            valid_mins   = [int(rec['Min_Price']) for rec in records if rec.get('Min_Price')]
            valid_maxs   = [int(rec['Max_Price']) for rec in records if rec.get('Max_Price')]

            if not valid_modals:
                continue

            # Median of valid prices — robust to outliers
            valid_modals.sort()
            n = len(valid_modals)
            median_modal = valid_modals[n // 2] if n % 2 == 1 else (valid_modals[n//2-1] + valid_modals[n//2]) // 2
            avg_min = round(sum(valid_mins) / len(valid_mins)) if valid_mins else median_modal
            avg_max = round(sum(valid_maxs) / len(valid_maxs)) if valid_maxs else median_modal

            latest = records[0]
            mandi_name = f"{latest.get('Market', 'N/A')}, {latest.get('District', '')}, {latest.get('State', '')}".strip(', ')
            arrival_date = latest.get('Arrival_Date', '')
            msp_info = MSP_DATA.get(commodity, {})

            results.append({
                'crop': commodity,
                'icon': msp_info.get('icon', '🌱'),
                'mandi': mandi_name,
                'state': latest.get('State', state_used),
                'district': latest.get('District', ''),
                'unit': 'qt',
                'price': median_modal,
                'min_price': avg_min,
                'max_price': avg_max,
                'msp': msp_info.get('msp'),
                'msp_year': msp_info.get('msp_year'),
                'arrival_date': arrival_date,
                'source': f'data.gov.in — Agmarknet Mandi ({state_used})',
                'mandi_count': n,
                'history': valid_modals[-7:]
            })
        except Exception as e:
            print(f'[Market] Failed to fetch {commodity}: {e}')
            continue
    return results



def _fallback_msp_prices():
    """Offline fallback using MSP 2025-26 reference prices.
    Shown only when data.gov.in API is unreachable.
    These are government MSP values — NOT live mandi prices.
    """
    fallback = [
        {'crop': 'Wheat',    'icon': '🌾', 'mandi': 'N/A (Offline)', 'msp': 2425, 'avg': 2425},
        {'crop': 'Rice',     'icon': '🍚', 'mandi': 'N/A (Offline)', 'msp': 2369, 'avg': 2369},
        {'crop': 'Mustard',  'icon': '🌻', 'mandi': 'N/A (Offline)', 'msp': 5950, 'avg': 5950},
        {'crop': 'Cotton',   'icon': '🏵️', 'mandi': 'N/A (Offline)', 'msp': 7710, 'avg': 7710},
        {'crop': 'Soyabean', 'icon': '🫘', 'mandi': 'N/A (Offline)', 'msp': 5328, 'avg': 5328},
        {'crop': 'Maize',    'icon': '🌽', 'mandi': 'N/A (Offline)', 'msp': 2400, 'avg': 2400},
        {'crop': 'Gram',     'icon': '🫘', 'mandi': 'N/A (Offline)', 'msp': 5650, 'avg': 5650},
        {'crop': 'Onion',    'icon': '🧅', 'mandi': 'N/A (Offline)', 'msp': None,  'avg': None},
        {'crop': 'Tomato',   'icon': '🍅', 'mandi': 'N/A (Offline)', 'msp': None,  'avg': None},
        {'crop': 'Potato',   'icon': '🥔', 'mandi': 'N/A (Offline)', 'msp': None,  'avg': None},
    ]
    prices = []
    for c in fallback:
        if c['avg'] is None:
            continue  # Skip non-MSP crops entirely when offline — no data to show
        prices.append({
            'crop': c['crop'], 'icon': c['icon'], 'mandi': c['mandi'],
            'unit': 'qt', 'price': c['avg'], 'msp': c['msp'], 'msp_year': '2025-26',
            'change': 0, 'source': 'MSP 2025-26 (Offline — data.gov.in unreachable)',
            'history': [c['avg']] * 7
        })
    return prices



@app.route('/api/market-prices', methods=['GET'])
def market_prices():
    """Mandi prices from data.gov.in Agmarknet dataset.
    Prices are updated daily (not real-time streaming).
    Optional ?state=Maharashtra to filter by state.
    Cached for 30 minutes per state.
    """
    state = request.args.get('state', '').strip() or None
    cache_key = state or 'national'

    if not hasattr(market_prices, '_cache'):
        market_prices._cache = {}

    cached = market_prices._cache.get(cache_key)
    if cached and (time.time() - cached['ts']) < 1800:
        return jsonify(cached['data'])

    now = datetime.now()
    live_prices = _fetch_live_prices(state=state)

    if live_prices and len(live_prices) >= 3:
        for p in live_prices:
            if p.get('msp'):
                p['change'] = round((p['price'] - p['msp']) / p['msp'] * 100, 1)
            else:
                spread = p.get('max_price', p['price']) - p.get('min_price', p['price'])
                p['change'] = round(spread / max(p['price'], 1) * 100, 1)

        location_label = state if state else 'India'
        result = {
            'prices': live_prices,
            'source': f'data.gov.in — Agmarknet Daily Mandi Prices ({location_label})',
            'msp_source': 'CCEA Govt. of India 2025-26 (pib.gov.in)',
            'updated': now.isoformat(),
            'update_freq': 'Daily (Agmarknet mandi auction records)',
            'location': location_label,
            'note': 'Prices reflect daily mandi auction records. Same crop can vary ₹200–₹1500 across regions. MSP = Govt. Minimum Support Price 2025-26.'
        }
    else:
        result = {
            'prices': _fallback_msp_prices(),
            'source': 'Ministry of Agriculture & Farmers Welfare, Govt. of India (MSP 2025-26)',
            'msp_source': 'CCEA Govt. of India 2025-26 (pib.gov.in)',
            'updated': now.isoformat(),
            'update_freq': 'Reference only — data.gov.in API unreachable',
            'location': state or 'India',
            'offline': True,
            'note': 'data.gov.in API unreachable. Showing MSP 2025-26 reference prices only. Not live mandi prices.'
        }

    market_prices._cache[cache_key] = {'data': result, 'ts': time.time()}
    return jsonify(result)



@app.route('/api/crop-guide', methods=['GET'])
def crop_guide():
    """Crop guide data — multilingual"""
    lang = request.args.get('lang', 'en')

    crops_data = {
        'en': [
            {
                "name": "Wheat", "icon": "🌾", "season": "Rabi (Oct-Mar)",
                "water": "4-6 irrigations", "soil": "Loamy, Clay Loam",
                "temp": "15-25°C", "duration": "120-150 days",
                "states": ["Punjab", "Haryana", "UP", "MP"],
                "tips": [
                    "Sow between Oct 25 - Nov 25 for best yield",
                    "First irrigation at 21 days (Crown Root Initiation)",
                    "Apply 120kg N, 60kg P, 40kg K per hectare",
                    "Use HD-2967 or PBW-550 varieties for high yield"
                ]
            },
            {
                "name": "Rice", "icon": "🍚", "season": "Kharif (Jun-Nov)",
                "water": "Standing water 5cm", "soil": "Clay, Silty Clay",
                "temp": "20-35°C", "duration": "90-150 days",
                "states": ["West Bengal", "UP", "Punjab", "Tamil Nadu"],
                "tips": [
                    "Transplant 20-25 day old seedlings",
                    "Maintain 5cm standing water till tillering",
                    "Apply Zinc Sulphate at 25kg/ha in Zinc-deficient soils",
                    "Use SRI method for 30-50% more yield with less water"
                ]
            },
            {
                "name": "Cotton", "icon": "🏵️", "season": "Kharif (Apr-Dec)",
                "water": "6-8 irrigations", "soil": "Black Cotton Soil",
                "temp": "25-35°C", "duration": "150-180 days",
                "states": ["Gujarat", "Maharashtra", "Telangana", "Rajasthan"],
                "tips": [
                    "Sow Bt cotton with 20% non-Bt refuge rows",
                    "First irrigation 3 weeks after sowing",
                    "Apply neem oil for sucking pest control",
                    "Pick cotton when bolls fully open and fluffy"
                ]
            },
            {
                "name": "Tomato", "icon": "🍅", "season": "Year-round",
                "water": "Drip irrigation best", "soil": "Well-drained Loamy",
                "temp": "20-30°C", "duration": "60-90 days",
                "states": ["Karnataka", "MP", "Andhra Pradesh", "Maharashtra"],
                "tips": [
                    "Transplant 25-30 day old seedlings at 60x45cm spacing",
                    "Stake plants for better fruit quality",
                    "Apply Trichoderma to prevent damping off",
                    "Harvest when 50% color develops for longer shelf life"
                ]
            },
            {
                "name": "Mustard", "icon": "🌻", "season": "Rabi (Oct-Feb)",
                "water": "2-3 irrigations", "soil": "Sandy Loam",
                "temp": "10-25°C", "duration": "110-140 days",
                "states": ["Rajasthan", "UP", "Haryana", "MP"],
                "tips": [
                    "Sow in first fortnight of October",
                    "First irrigation at 25-30 DAS",
                    "Apply Sulphur 40kg/ha for higher oil content",
                    "Spray Imidacloprid for aphid control"
                ]
            },
            {
                "name": "Sugarcane", "icon": "🎋", "season": "Feb-Mar / Oct",
                "water": "Frequent irrigation", "soil": "Deep Loamy",
                "temp": "20-35°C", "duration": "10-16 months",
                "states": ["UP", "Maharashtra", "Karnataka", "Tamil Nadu"],
                "tips": [
                    "Use 3-bud setts treated with Carbendazim",
                    "Earthing up at 90 and 120 days is critical",
                    "Trash mulching retains moisture and suppresses weeds",
                    "Harvest at 10-12 months for maximum sugar recovery"
                ]
            },
        ],
        'hi': [
            {
                "name": "गेहूं", "icon": "🌾", "season": "रबी (अक्टू-मार्च)",
                "water": "4-6 सिंचाई", "soil": "दोमट, चिकनी दोमट",
                "temp": "15-25°C", "duration": "120-150 दिन",
                "states": ["पंजाब", "हरियाणा", "उत्तर प्रदेश", "मध्य प्रदेश"],
                "tips": [
                    "सर्वोत्तम उपज के लिए 25 अक्टूबर - 25 नवंबर के बीच बुवाई करें",
                    "21 दिन पर पहली सिंचाई (क्राउन रूट इनिशिएशन)",
                    "प्रति हेक्टेयर 120kg N, 60kg P, 40kg K डालें",
                    "अधिक उपज के लिए HD-2967 या PBW-550 किस्में उपयोग करें"
                ]
            },
            {
                "name": "चावल", "icon": "🍚", "season": "खरीफ (जून-नवं)",
                "water": "5cm खड़ा पानी", "soil": "चिकनी मिट्टी",
                "temp": "20-35°C", "duration": "90-150 दिन",
                "states": ["पश्चिम बंगाल", "उत्तर प्रदेश", "पंजाब", "तमिलनाडु"],
                "tips": [
                    "20-25 दिन की पौध रोपें",
                    "कल्ले निकलने तक 5cm पानी बनाए रखें",
                    "जिंक की कमी वाली मिट्टी में 25kg/ha जिंक सल्फेट डालें",
                    "कम पानी में 30-50% अधिक उपज के लिए SRI विधि अपनाएं"
                ]
            },
            {
                "name": "कपास", "icon": "🏵️", "season": "खरीफ (अप्रैल-दिसं)",
                "water": "6-8 सिंचाई", "soil": "काली कपास मिट्टी",
                "temp": "25-35°C", "duration": "150-180 दिन",
                "states": ["गुजरात", "महाराष्ट्र", "तेलंगाना", "राजस्थान"],
                "tips": [
                    "Bt कपास के साथ 20% गैर-Bt रिफ्यूज पंक्तियां लगाएं",
                    "बुवाई के 3 सप्ताह बाद पहली सिंचाई",
                    "चूसक कीट नियंत्रण के लिए नीम तेल लगाएं",
                    "जब टिंडे पूरी तरह खुलें तब चुनाई करें"
                ]
            },
            {
                "name": "टमाटर", "icon": "🍅", "season": "साल भर",
                "water": "ड्रिप सिंचाई सर्वोत्तम", "soil": "अच्छी जल निकासी वाली दोमट",
                "temp": "20-30°C", "duration": "60-90 दिन",
                "states": ["कर्नाटक", "मध्य प्रदेश", "आंध्र प्रदेश", "महाराष्ट्र"],
                "tips": [
                    "25-30 दिन की पौध 60x45cm दूरी पर रोपें",
                    "बेहतर फल गुणवत्ता के लिए पौधों को सहारा दें",
                    "डैम्पिंग ऑफ रोकने के लिए ट्राइकोडर्मा डालें",
                    "लंबी शेल्फ लाइफ के लिए 50% रंग आने पर तोड़ें"
                ]
            },
            {
                "name": "सरसों", "icon": "🌻", "season": "रबी (अक्टू-फर)",
                "water": "2-3 सिंचाई", "soil": "बलुई दोमट",
                "temp": "10-25°C", "duration": "110-140 दिन",
                "states": ["राजस्थान", "उत्तर प्रदेश", "हरियाणा", "मध्य प्रदेश"],
                "tips": [
                    "अक्टूबर के पहले पखवाड़े में बुवाई करें",
                    "बुवाई के 25-30 दिन बाद पहली सिंचाई",
                    "अधिक तेल के लिए 40kg/ha सल्फर डालें",
                    "एफिड नियंत्रण के लिए इमिडाक्लोप्रिड स्प्रे करें"
                ]
            },
            {
                "name": "गन्ना", "icon": "🎋", "season": "फर-मार्च / अक्टू",
                "water": "बार-बार सिंचाई", "soil": "गहरी दोमट",
                "temp": "20-35°C", "duration": "10-16 महीने",
                "states": ["उत्तर प्रदेश", "महाराष्ट्र", "कर्नाटक", "तमिलनाडु"],
                "tips": [
                    "कार्बेन्डाजिम से उपचारित 3-आंख वाले टुकड़े उपयोग करें",
                    "90 और 120 दिन पर मिट्टी चढ़ाना अत्यंत जरूरी",
                    "ट्रैश मल्चिंग से नमी बनी रहती है और खरपतवार दबते हैं",
                    "अधिकतम चीनी रिकवरी के लिए 10-12 महीने पर कटाई करें"
                ]
            },
        ],
        'te': [
            {
                "name": "గోధుమ", "icon": "🌾", "season": "రబీ (అక్టో-మార్చి)",
                "water": "4-6 నీటి తడులు", "soil": "గరుగు, బంక మట్టి",
                "temp": "15-25°C", "duration": "120-150 రోజులు",
                "states": ["పంజాబ్", "హర్యానా", "ఉత్తర ప్రదేశ్", "మధ్య ప్రదేశ్"],
                "tips": [
                    "మంచి దిగుబడి కోసం అక్టోబర్ 25 - నవంబర్ 25 మధ్య విత్తండి",
                    "21 రోజులకు మొదటి నీటి తడి (క్రౌన్ రూట్ ఇనిషియేషన్)",
                    "హెక్టారుకు 120kg N, 60kg P, 40kg K వేయండి",
                    "ఎక్కువ దిగుబడి కోసం HD-2967 లేదా PBW-550 రకాలు వాడండి"
                ]
            },
            {
                "name": "వరి", "icon": "🍚", "season": "ఖరీఫ్ (జూన్-నవం)",
                "water": "5cm నిలువ నీరు", "soil": "బంక మట్టి",
                "temp": "20-35°C", "duration": "90-150 రోజులు",
                "states": ["పశ్చిమ బెంగాల్", "ఉత్తర ప్రదేశ్", "పంజాబ్", "తమిళనాడు"],
                "tips": [
                    "20-25 రోజుల నారును నాటండి",
                    "పిలకలు వచ్చేవరకు 5cm నీరు నిలపండి",
                    "జింక్ లోపం ఉన్న నేలల్లో 25kg/ha జింక్ సల్ఫేట్ వేయండి",
                    "తక్కువ నీటితో 30-50% ఎక్కువ దిగుబడి కోసం SRI పద్ధతి వాడండి"
                ]
            },
            {
                "name": "పత్తి", "icon": "🏵️", "season": "ఖరీఫ్ (ఏప్రిల్-డిసెం)",
                "water": "6-8 నీటి తడులు", "soil": "నల్ల రేగడి మట్టి",
                "temp": "25-35°C", "duration": "150-180 రోజులు",
                "states": ["గుజరాత్", "మహారాష్ట్ర", "తెలంగాణ", "రాజస్థాన్"],
                "tips": [
                    "Bt పత్తితో 20% నాన్-Bt ఆశ్రయ వరుసలు నాటండి",
                    "విత్తిన 3 వారాల తర్వాత మొదటి నీటి తడి",
                    "పీల్చే పురుగుల నియంత్రణకు వేప నూనె పిచికారీ చేయండి",
                    "కాయలు పూర్తిగా విచ్చుకున్నప్పుడు పత్తి ఏరండి"
                ]
            },
            {
                "name": "టమాటా", "icon": "🍅", "season": "ఏడాది పొడవునా",
                "water": "డ్రిప్ ఇరిగేషన్ ఉత్తమం", "soil": "నీరు బాగా ఇంకే గరుగు మట్టి",
                "temp": "20-30°C", "duration": "60-90 రోజులు",
                "states": ["కర్ణాటక", "మధ్య ప్రదేశ్", "ఆంధ్ర ప్రదేశ్", "మహారాష్ట్ర"],
                "tips": [
                    "25-30 రోజుల నారును 60x45cm దూరంలో నాటండి",
                    "మంచి పండ్ల నాణ్యత కోసం మొక్కలకు ఊతం ఇవ్వండి",
                    "డ్యాంపింగ్ ఆఫ్ నివారణకు ట్రైకోడెర్మా వాడండి",
                    "ఎక్కువ షెల్ఫ్ లైఫ్ కోసం 50% రంగు వచ్చినప్పుడు కోయండి"
                ]
            },
            {
                "name": "ఆవాలు", "icon": "🌻", "season": "రబీ (అక్టో-ఫిబ్ర)",
                "water": "2-3 నీటి తడులు", "soil": "ఇసుక గరుగు మట్టి",
                "temp": "10-25°C", "duration": "110-140 రోజులు",
                "states": ["రాజస్థాన్", "ఉత్తర ప్రదేశ్", "హర్యానా", "మధ్య ప్రదేశ్"],
                "tips": [
                    "అక్టోబర్ మొదటి పక్షంలో విత్తండి",
                    "విత్తిన 25-30 రోజులకు మొదటి నీటి తడి",
                    "ఎక్కువ నూనె కోసం 40kg/ha సల్ఫర్ వేయండి",
                    "అఫిడ్ నియంత్రణకు ఇమిడాక్లోప్రిడ్ పిచికారీ చేయండి"
                ]
            },
            {
                "name": "చెరకు", "icon": "🎋", "season": "ఫిబ్ర-మార్చి / అక్టో",
                "water": "తరచుగా నీటి తడులు", "soil": "లోతైన గరుగు మట్టి",
                "temp": "20-35°C", "duration": "10-16 నెలలు",
                "states": ["ఉత్తర ప్రదేశ్", "మహారాష్ట్ర", "కర్ణాటక", "తమిళనాడు"],
                "tips": [
                    "కార్బెండజిమ్‌తో చికిత్స చేసిన 3-కణుపుల ముక్కలు వాడండి",
                    "90 మరియు 120 రోజులకు మట్టి ఎగదోయడం చాలా ముఖ్యం",
                    "ట్రాష్ మల్చింగ్ తేమ నిలుపుతుంది, కలుపు అణచివేస్తుంది",
                    "గరిష్ట చక్కెర రికవరీ కోసం 10-12 నెలలకు కోయండి"
                ]
            },
        ]
    }

    crops = crops_data.get(lang, crops_data['en'])
    return jsonify({'crops': crops})


@app.route('/api/pest-solutions', methods=['GET'])
def pest_solutions():
    """Pest and disease solutions — multilingual"""
    lang = request.args.get('lang', 'en')

    # Labels for UI text in pest cards
    labels = {
        'en': {'affects': 'Affects', 'ask_ai': '🤖 Ask AI about'},
        'hi': {'affects': 'प्रभावित फसलें', 'ask_ai': '🤖 AI से पूछें'},
        'te': {'affects': 'ప్రభావిత పంటలు', 'ask_ai': '🤖 AI ని అడగండి'},
    }

    pests_data = {
        'en': [
            {
                "name": "Aphids", "icon": "🐛", "severity": "high",
                "crops": ["Mustard", "Wheat", "Vegetables"],
                "symptoms": "Curling of leaves, sticky honeydew on leaf surface, stunted growth",
                "solutions": [
                    {"type": "organic", "method": "Spray neem oil (5ml/L) every 10-15 days"},
                    {"type": "organic", "method": "Release ladybugs (natural predators) in the field"},
                    {"type": "chemical", "method": "Spray Imidacloprid 17.8% SL (0.3ml/L)"},
                    {"type": "preventive", "method": "Yellow sticky traps at field borders"},
                ]
            },
            {
                "name": "Bollworm", "icon": "🐛", "severity": "critical",
                "crops": ["Cotton", "Tomato", "Chickpea"],
                "symptoms": "Holes in bolls/fruits, frass visible, damaged squares and flowers",
                "solutions": [
                    {"type": "organic", "method": "Install pheromone traps (5/ha) for monitoring"},
                    {"type": "organic", "method": "Spray Bt (Bacillus thuringiensis) at 1g/L"},
                    {"type": "chemical", "method": "Spray Emamectin Benzoate 5% SG (0.4g/L)"},
                    {"type": "preventive", "method": "Grow marigold as trap crop on borders"},
                ]
            },
            {
                "name": "Leaf Blast", "icon": "🦠", "severity": "high",
                "crops": ["Rice", "Wheat", "Pearl Millet"],
                "symptoms": "Diamond-shaped lesions on leaves with grey center, drying of leaves",
                "solutions": [
                    {"type": "organic", "method": "Use resistant varieties (Pusa Basmati 1121)"},
                    {"type": "chemical", "method": "Spray Tricyclazole 75% WP (0.6g/L)"},
                    {"type": "chemical", "method": "Spray Isoprothiolane 40% EC (1.5ml/L)"},
                    {"type": "preventive", "method": "Avoid excess nitrogen, maintain proper spacing"},
                ]
            },
            {
                "name": "Whitefly", "icon": "🪰", "severity": "medium",
                "crops": ["Cotton", "Tomato", "Chilli", "Brinjal"],
                "symptoms": "Yellowing of leaves, sooty mould, leaf curling (transmits viruses)",
                "solutions": [
                    {"type": "organic", "method": "Spray neem seed kernel extract (5%)"},
                    {"type": "organic", "method": "Yellow sticky traps (12/acre)"},
                    {"type": "chemical", "method": "Spray Diafenthiuron 50% WP (1g/L)"},
                    {"type": "preventive", "method": "Remove and destroy alternate host weeds"},
                ]
            },
            {
                "name": "Late Blight", "icon": "🦠", "severity": "critical",
                "crops": ["Potato", "Tomato"],
                "symptoms": "Water-soaked lesions on leaves, white fungal growth under leaves, rapid wilting",
                "solutions": [
                    {"type": "organic", "method": "Spray Bordeaux mixture (1%) preventively"},
                    {"type": "chemical", "method": "Spray Mancozeb 75% WP (2.5g/L) at first sign"},
                    {"type": "chemical", "method": "Spray Cymoxanil + Mancozeb (3g/L) for severe cases"},
                    {"type": "preventive", "method": "Use certified disease-free seed tubers"},
                ]
            },
            {
                "name": "Stem Borer", "icon": "🐛", "severity": "high",
                "crops": ["Rice", "Sugarcane", "Maize"],
                "symptoms": "Dead heart in vegetative stage, white ear in reproductive stage",
                "solutions": [
                    {"type": "organic", "method": "Release Trichogramma wasps (8 cards/ha)"},
                    {"type": "organic", "method": "Light traps to attract and kill adult moths"},
                    {"type": "chemical", "method": "Apply Cartap hydrochloride 4G granules in leaf whorl"},
                    {"type": "preventive", "method": "Early planting and removal of stubbles after harvest"},
                ]
            },
        ],
        'hi': [
            {
                "name": "एफिड (माहू)", "icon": "🐛", "severity": "high",
                "crops": ["सरसों", "गेहूं", "सब्जियां"],
                "symptoms": "पत्तियों का मुड़ना, पत्ती सतह पर चिपचिपा रस, बौना विकास",
                "solutions": [
                    {"type": "organic", "method": "हर 10-15 दिन नीम तेल (5ml/L) का छिड़काव"},
                    {"type": "organic", "method": "खेत में लेडीबग (प्राकृतिक शत्रु) छोड़ें"},
                    {"type": "chemical", "method": "इमिडाक्लोप्रिड 17.8% SL (0.3ml/L) स्प्रे करें"},
                    {"type": "preventive", "method": "खेत की सीमा पर पीले चिपचिपे जाल लगाएं"},
                ]
            },
            {
                "name": "बॉलवर्म", "icon": "🐛", "severity": "critical",
                "crops": ["कपास", "टमाटर", "चना"],
                "symptoms": "टिंडों/फलों में छेद, फ्रास दिखना, क्षतिग्रस्त फूल",
                "solutions": [
                    {"type": "organic", "method": "फेरोमोन ट्रैप (5/हेक्टेयर) लगाएं"},
                    {"type": "organic", "method": "Bt (बैसिलस थुरिंजिएंसिस) 1g/L पर स्प्रे करें"},
                    {"type": "chemical", "method": "इमामेक्टिन बेंजोएट 5% SG (0.4g/L) स्प्रे करें"},
                    {"type": "preventive", "method": "किनारों पर गेंदा ट्रैप फसल के रूप में उगाएं"},
                ]
            },
            {
                "name": "ब्लास्ट रोग", "icon": "🦠", "severity": "high",
                "crops": ["चावल", "गेहूं", "बाजरा"],
                "symptoms": "पत्तियों पर हीरे के आकार के धब्बे, पत्तियों का सूखना",
                "solutions": [
                    {"type": "organic", "method": "प्रतिरोधी किस्में (पूसा बासमती 1121) उपयोग करें"},
                    {"type": "chemical", "method": "ट्राइसाइक्लाजोल 75% WP (0.6g/L) स्प्रे करें"},
                    {"type": "chemical", "method": "आइसोप्रोथियोलेन 40% EC (1.5ml/L) स्प्रे करें"},
                    {"type": "preventive", "method": "अधिक नाइट्रोजन से बचें, उचित दूरी बनाए रखें"},
                ]
            },
            {
                "name": "सफ़ेद मक्खी", "icon": "🪰", "severity": "medium",
                "crops": ["कपास", "टमाटर", "मिर्च", "बैंगन"],
                "symptoms": "पत्तियों का पीलापन, काली फफूंद, पत्ती मुड़ना (वायरस फैलाती है)",
                "solutions": [
                    {"type": "organic", "method": "नीम बीज गिरी अर्क (5%) का छिड़काव"},
                    {"type": "organic", "method": "पीले चिपचिपे ट्रैप (12/एकड़)"},
                    {"type": "chemical", "method": "डायफेंथ्यूरॉन 50% WP (1g/L) स्प्रे करें"},
                    {"type": "preventive", "method": "वैकल्पिक मेजबान खरपतवार हटाकर नष्ट करें"},
                ]
            },
            {
                "name": "लेट ब्लाइट", "icon": "🦠", "severity": "critical",
                "crops": ["आलू", "टमाटर"],
                "symptoms": "पत्तियों पर पानी जैसे धब्बे, नीचे सफेद फफूंद, तेज मुरझाना",
                "solutions": [
                    {"type": "organic", "method": "बोर्डो मिश्रण (1%) का निवारक छिड़काव"},
                    {"type": "chemical", "method": "पहले लक्षण पर मैंकोजेब 75% WP (2.5g/L) स्प्रे करें"},
                    {"type": "chemical", "method": "गंभीर मामलों में सिमॉक्सनिल + मैंकोजेब (3g/L)"},
                    {"type": "preventive", "method": "प्रमाणित रोग-मुक्त बीज कंद उपयोग करें"},
                ]
            },
            {
                "name": "तना छेदक", "icon": "🐛", "severity": "high",
                "crops": ["चावल", "गन्ना", "मक्का"],
                "symptoms": "वानस्पतिक अवस्था में डेड हार्ट, प्रजनन अवस्था में सफेद बाली",
                "solutions": [
                    {"type": "organic", "method": "ट्राइकोग्रामा ततैया (8 कार्ड/हेक्टेयर) छोड़ें"},
                    {"type": "organic", "method": "वयस्क पतंगों को आकर्षित करने हेतु प्रकाश जाल"},
                    {"type": "chemical", "method": "पत्ती घुंडी में कार्टैप हाइड्रोक्लोराइड 4G दाने डालें"},
                    {"type": "preventive", "method": "जल्दी बुवाई करें और कटाई बाद ठूंठ हटाएं"},
                ]
            },
        ],
        'te': [
            {
                "name": "అఫిడ్స్ (పేనుబంక)", "icon": "🐛", "severity": "high",
                "crops": ["ఆవాలు", "గోధుమ", "కూరగాయలు"],
                "symptoms": "ఆకులు ముడుచుకోవడం, ఆకులపై జిగురు రసం, ఎదుగుదల తగ్గడం",
                "solutions": [
                    {"type": "organic", "method": "ప్రతి 10-15 రోజులకు వేప నూనె (5ml/L) పిచికారీ"},
                    {"type": "organic", "method": "పొలంలో లేడీబగ్స్ (సహజ శత్రువులు) వదలండి"},
                    {"type": "chemical", "method": "ఇమిడాక్లోప్రిడ్ 17.8% SL (0.3ml/L) పిచికారీ"},
                    {"type": "preventive", "method": "పొలం అంచులలో పసుపు అంటు ట్రాపులు పెట్టండి"},
                ]
            },
            {
                "name": "బోల్‌వార్మ్", "icon": "🐛", "severity": "critical",
                "crops": ["పత్తి", "టమాటా", "శనగ"],
                "symptoms": "కాయల్లో/పండ్లలో రంధ్రాలు, మలం కనిపించడం, దెబ్బతిన్న పువ్వులు",
                "solutions": [
                    {"type": "organic", "method": "ఫెరోమోన్ ట్రాప్‌లు (5/హెక్టారు) పెట్టండి"},
                    {"type": "organic", "method": "Bt (బాసిల్లస్ థురింజియెన్సిస్) 1g/L పిచికారీ"},
                    {"type": "chemical", "method": "ఎమామెక్టిన్ బెంజోయేట్ 5% SG (0.4g/L) పిచికారీ"},
                    {"type": "preventive", "method": "అంచుల్లో బంతి పూలు ట్రాప్ పంటగా వేయండి"},
                ]
            },
            {
                "name": "ఆకు బ్లాస్ట్", "icon": "🦠", "severity": "high",
                "crops": ["వరి", "గోధుమ", "సజ్జ"],
                "symptoms": "ఆకులపై వజ్రాకార మచ్చలు, బూడిద రంగు కేంద్రం, ఆకులు ఎండిపోవడం",
                "solutions": [
                    {"type": "organic", "method": "నిరోధక రకాలు (పూసా బాస్మతి 1121) వాడండి"},
                    {"type": "chemical", "method": "ట్రైసైక్లాజోల్ 75% WP (0.6g/L) పిచికారీ"},
                    {"type": "chemical", "method": "ఐసోప్రోథియోలేన్ 40% EC (1.5ml/L) పిచికారీ"},
                    {"type": "preventive", "method": "అధిక నత్రజని మానండి, సరైన దూరం పాటించండి"},
                ]
            },
            {
                "name": "తెల్ల ఈగ", "icon": "🪰", "severity": "medium",
                "crops": ["పత్తి", "టమాటా", "మిర్చి", "వంకాయ"],
                "symptoms": "ఆకులు పసుపు రంగుకు మారడం, నల్ల బూజు, ఆకుల ముడుచుకోవడం",
                "solutions": [
                    {"type": "organic", "method": "వేప గింజల గుజ్జు కషాయం (5%) పిచికారీ"},
                    {"type": "organic", "method": "పసుపు అంటు ట్రాపులు (12/ఎకరం)"},
                    {"type": "chemical", "method": "డయాఫెంథ్యూరాన్ 50% WP (1g/L) పిచికారీ"},
                    {"type": "preventive", "method": "ప్రత్యామ్నాయ ఆతిథేయ కలుపు మొక్కలు తొలగించండి"},
                ]
            },
            {
                "name": "లేట్ బ్లైట్", "icon": "🦠", "severity": "critical",
                "crops": ["బంగాళాదుంప", "టమాటా"],
                "symptoms": "ఆకులపై నీటి మచ్చలు, క్రింద తెల్ల బూజు, వేగంగా వాడిపోవడం",
                "solutions": [
                    {"type": "organic", "method": "బోర్డో మిశ్రమం (1%) నివారణగా పిచికారీ"},
                    {"type": "chemical", "method": "మొదటి సంకేతంలో మాంకోజెబ్ 75% WP (2.5g/L) పిచికారీ"},
                    {"type": "chemical", "method": "తీవ్ర సమస్యలకు సైమోక్సానిల్ + మాంకోజెబ్ (3g/L)"},
                    {"type": "preventive", "method": "ధృవీకరించిన రోగ-రహిత విత్తన దుంపలు వాడండి"},
                ]
            },
            {
                "name": "కాండం తొలుచు పురుగు", "icon": "🐛", "severity": "high",
                "crops": ["వరి", "చెరకు", "మొక్కజొన్న"],
                "symptoms": "మొక్క దశలో డెడ్ హార్ట్, పునరుత్పత్తి దశలో తెల్ల కంకి",
                "solutions": [
                    {"type": "organic", "method": "ట్రైకోగ్రామా కందిరీగలు (8 కార్డులు/హెక్టారు) వదలండి"},
                    {"type": "organic", "method": "పెద్ద చిమ్మటలను ఆకర్షించేందుకు కాంతి ట్రాపులు"},
                    {"type": "chemical", "method": "ఆకు గొట్టంలో కార్టాప్ హైడ్రోక్లోరైడ్ 4G గుళికలు"},
                    {"type": "preventive", "method": "ముందుగా నాటండి, కోత తర్వాత మోళ్ళు తొలగించండి"},
                ]
            },
        ]
    }

    pest_labels = labels.get(lang, labels['en'])
    pests = pests_data.get(lang, pests_data['en'])
    return jsonify({'pests': pests, 'labels': pest_labels})


@app.route('/api/popular', methods=['GET'])
def popular_questions():
    lang = request.args.get('lang', 'en')

    popular_data = {
        'en': [
            {
                'name': 'Weather', 'icon': '🌤️',
                'questions': [
                    "What is the weather forecast for wheat season?",
                    "How does climate change affect Indian farming?",
                    "Best time to sow paddy in monsoon?",
                ]
            },
            {
                'name': 'Market Prices', 'icon': '💰',
                'questions': [
                    "What is the current wheat price per quintal?",
                    "Best time to sell tomatoes for profit?",
                    "How to get MSP for my paddy crop?",
                ]
            },
            {
                'name': 'Crop Guide', 'icon': '🌱',
                'questions': [
                    "What fertilizer is best during flowering stage?",
                    "How to improve soil health for better yield?",
                    "What is the recommended irrigation for wheat?",
                ]
            },
            {
                'name': 'Pest Solutions', 'icon': '🐛',
                'questions': [
                    "How to control aphids in mustard crop?",
                    "What is the treatment for leaf spot in tomato?",
                    "How to prevent fruit borer in brinjal?",
                ]
            }
        ],
        'hi': [
            {
                'name': 'मौसम', 'icon': '🌤️',
                'questions': [
                    "गेहूं के मौसम का मौसम पूर्वानुमान क्या है?",
                    "जलवायु परिवर्तन भारतीय खेती को कैसे प्रभावित करता है?",
                    "मानसून में धान बोने का सबसे अच्छा समय?",
                ]
            },
            {
                'name': 'मंडी भाव', 'icon': '💰',
                'questions': [
                    "प्रति क्विंटल गेहूं का वर्तमान भाव क्या है?",
                    "लाभ के लिए टमाटर बेचने का सबसे अच्छा समय?",
                    "मेरी धान की फसल के लिए MSP कैसे मिलेगा?",
                ]
            },
            {
                'name': 'फसल गाइड', 'icon': '🌱',
                'questions': [
                    "फूल आने पर कौन सा उर्वरक सबसे अच्छा है?",
                    "बेहतर उपज के लिए मिट्टी का स्वास्थ्य कैसे सुधारें?",
                    "गेहूं के लिए अनुशंसित सिंचाई क्या है?",
                ]
            },
            {
                'name': 'कीट समाधान', 'icon': '🐛',
                'questions': [
                    "सरसों में एफिड कैसे नियंत्रित करें?",
                    "टमाटर में पत्ती धब्बा का उपचार क्या है?",
                    "बैंगन में फल छेदक कैसे रोकें?",
                ]
            }
        ],
        'te': [
            {
                'name': 'వాతావరణం', 'icon': '🌤️',
                'questions': [
                    "గోధుమ సీజన్‌కు వాతావరణ అంచనా ఏమిటి?",
                    "జలవాయు మార్పు భారత వ్యవసాయాన్ని ఎలా ప్రభావితం చేస్తుంది?",
                    "వర్షాకాలంలో వరి విత్తడానికి ఉత్తమ సమయం?",
                ]
            },
            {
                'name': 'మార్కెట్ ధరలు', 'icon': '💰',
                'questions': [
                    "క్వింటాలుకు ప్రస్తుత గోధుమ ధర ఎంత?",
                    "లాభం కోసం టమాటాలు అమ్మడానికి ఉత్తమ సమయం?",
                    "నా వరి పంటకు MSP ఎలా పొందాలి?",
                ]
            },
            {
                'name': 'పంట గైడ్', 'icon': '🌱',
                'questions': [
                    "పూత దశలో ఏ ఎరువు ఉత్తమం?",
                    "మంచి దిగుబడి కోసం నేల ఆరోగ్యం ఎలా మెరుగుపరచాలి?",
                    "గోధుమకు సిఫార్సు చేసిన నీటి తడి ఏమిటి?",
                ]
            },
            {
                'name': 'పురుగుల పరిష్కారాలు', 'icon': '🐛',
                'questions': [
                    "ఆవాలో అఫిడ్స్ ఎలా నియంత్రించాలి?",
                    "టమాటాలో ఆకు మచ్చ చికిత్స ఏమిటి?",
                    "వంకాయలో పండు తొలుచు పురుగు ఎలా నివారించాలి?",
                ]
            }
        ]
    }

    categories = popular_data.get(lang, popular_data['en'])
    return jsonify({'categories': categories})


@app.route('/api/schemes', methods=['GET'])
def schemes():
    """Government schemes data — multilingual"""
    lang = request.args.get('lang', 'en')

    schemes_data = {
        'en': [
            {"name": "PM-KISAN", "icon": "💸", "desc": "₹6,000/year income support for farmers"},
            {"name": "PM Fasal Bima Yojana", "icon": "🛡️", "desc": "Crop insurance against natural calamities"},
            {"name": "Soil Health Card", "icon": "🧪", "desc": "Free soil testing and nutrient recommendations"},
            {"name": "Kisan Credit Card (KCC)", "icon": "💳", "desc": "Low interest loans for agricultural needs"},
            {"name": "e-NAM", "icon": "📱", "desc": "National Agriculture Market for better prices"},
            {"name": "Paramparagat Krishi Vikas", "icon": "🍂", "desc": "Promotion of organic farming"},
        ],
        'hi': [
            {"name": "PM-KISAN", "icon": "💸", "desc": "किसानों को ₹6,000/वर्ष आय सहायता"},
            {"name": "PM फसल बीमा योजना", "icon": "🛡️", "desc": "प्राकृतिक आपदाओं से फसल बीमा"},
            {"name": "मृदा स्वास्थ्य कार्ड", "icon": "🧪", "desc": "मुफ्त मिट्टी परीक्षण और पोषक तत्व सुझाव"},
            {"name": "किसान क्रेडिट कार्ड (KCC)", "icon": "💳", "desc": "कृषि आवश्यकताओं के लिए कम ब्याज ऋण"},
            {"name": "e-NAM", "icon": "📱", "desc": "बेहतर कीमतों के लिए राष्ट्रीय कृषि बाजार"},
            {"name": "परंपरागत कृषि विकास", "icon": "🍂", "desc": "जैविक खेती को बढ़ावा"},
        ],
        'te': [
            {"name": "PM-KISAN", "icon": "💸", "desc": "రైతులకు ₹6,000/సంవత్సరం ఆదాయ సహాయం"},
            {"name": "PM ఫసల్ బీమా యోజన", "icon": "🛡️", "desc": "ప్రకృతి విపత్తుల నుండి పంట బీమా"},
            {"name": "నేల ఆరోగ్య కార్డు", "icon": "🧪", "desc": "ఉచిత నేల పరీక్ష మరియు పోషక సిఫార్సులు"},
            {"name": "కిసాన్ క్రెడిట్ కార్డ్ (KCC)", "icon": "💳", "desc": "వ్యవసాయ అవసరాలకు తక్కువ వడ్డీ రుణాలు"},
            {"name": "e-NAM", "icon": "📱", "desc": "మంచి ధరల కోసం జాతీయ వ్యవసాయ మార్కెట్"},
            {"name": "పరంపరాగత కృషి వికాస్", "icon": "🍂", "desc": "సేంద్రియ వ్యవసాయ ప్రోత్సాహం"},
        ]
    }

    return jsonify({'schemes': schemes_data.get(lang, schemes_data['en'])})


@app.route('/api/stats', methods=['GET'])
def stats():
    """Knowledge base stats"""
    # In a real app, these would be counted dynamically
    return jsonify({
        'qa_pairs': 2450,
        'crops': 18,
        'states': 29,
        'last_updated': datetime.now().strftime('%d %b %Y')
    })

# ── CROP PRICE PREDICTION & ADVISORY ────────────────────
from services.price_predictor import predict_prices, generate_advisory, get_available_crops


@app.route('/api/price-prediction', methods=['GET'])
def price_prediction():
    """Predict future crop prices using historical trend analysis.
       Query: ?crop=Wheat&days=30
    """
    crop = request.args.get('crop', 'Wheat')
    days = min(int(request.args.get('days', 30)), 90)
    state = request.args.get('state', '').strip() or None

    available = get_available_crops()
    if crop not in available:
        return jsonify({'error': f'Crop not found. Available: {", ".join(available)}'}), 400

    try:
        result = predict_prices(crop, forecast_days=days, state=state)
        if not result:
            return jsonify({'error': 'Prediction failed'}), 500

        history_data = result['history'][-90:]
        return jsonify({
            'crop': result['crop'],
            'icon': result['icon'],
            'msp': result['msp'],
            'msp_year': '2025-26',
            'current_price': result['current_price'],
            'predicted_price': result['predicted_price'],
            'history': history_data,
            'prediction': result['prediction'],
            'moving_avg_30': result['moving_avg_30'],
            'moving_avg_90': result['moving_avg_90'],
            'trend': result['trend'],
            'slope_per_day': result['slope_per_day'],
            'confidence': result['confidence'],
            'forecast_days': result['forecast_days'],
            'source': result.get('source', 'AI Model'),
            'last_updated': result.get('last_updated'),
            'data_points': len(history_data),
            'location': state or 'India',
            'methodology': {
                'model': 'Weighted Moving Average + Linear Regression',
                'features': [
                    'WMA-30 (30-day weighted moving average)',
                    'Linear regression slope (trend direction)',
                    'Seasonal pattern (rabi/kharif cycle)',
                    'MSP reference 2025-26 (CCEA Govt. of India)',
                    'Confidence band (volatility-based range)'
                ],
                'accuracy_note': '±~15% trend estimate. Most reliable for 7-14 days. Not accurate for policy, rainfall or export shocks.',
                'data_source': result.get('source', 'AI Model'),
                'interpolation': 'Linear interpolation for missing dates in mandi data'
            },
            'available_crops': available,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f'[PricePrediction] Error: {e}')
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/price-advisory', methods=['GET'])
def price_advisory():
    """Get buy/sell/hold advisory for all crops or a specific crop.
       Query: ?crop=Wheat (optional) &state=Maharashtra (optional)
    """
    crop = request.args.get('crop', None)
    state = request.args.get('state', '').strip() or None

    try:
        advisories = generate_advisory(crop, state=state)
        return jsonify({
            'advisories': advisories,
            'count': len(advisories),
            'location': state or 'India',
            'msp_source': 'CCEA Govt. of India 2025-26 (pib.gov.in)',
            'timestamp': datetime.now().isoformat(),
            'disclaimer': 'MSP values are CCEA 2025-26 approved. Price forecasts are model trend estimates (±~15%), not published by any government authority. Consult nearest APMC before selling.'
        })
    except Exception as e:
        print(f'[PriceAdvisory] Error: {e}')
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ── Pre-load services at import time (for gunicorn) ─────
print("[STARTUP] Pre-loading services...")
try:
    get_faiss_searcher()
except Exception as e:
    print(f"[STARTUP][WARN] FAISS pre-load failed: {e}")
    traceback.print_exc()

try:
    get_watsonx_service()
except Exception as e:
    print(f"[STARTUP][WARN] AI service pre-load failed: {e}")
    traceback.print_exc()

print("[STARTUP] Service pre-load complete.")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("  KrishiMind AI — API Server")
    print(f"  Port: {port}")
    print("=" * 50)

    print(f"\n  Dashboard: http://localhost:{port}/dashboard/")
    print(f"  API:       http://localhost:{port}/api/health")
    print("=" * 50)

    app.run(host='0.0.0.0', port=port, debug=False)
