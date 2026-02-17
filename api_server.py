"""
KrishiMind AI — REST API Server
Wraps existing FAISS + Gemini services for the new dashboard
"""

import sys
import os
import time
import json
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
app.secret_key = os.urandom(24)  # Secure session key
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


@app.route('/api/popular', methods=['GET'])
def popular_questions():
    return jsonify({
        'categories': [
            {
                'name': 'Weather',
                'icon': '🌤️',
                'questions': [
                    "What is the weather forecast for wheat season?",
                    "How does climate change affect Indian farming?",
                    "Best time to sow paddy in monsoon?",
                ]
            },
            {
                'name': 'Market Prices',
                'icon': '💰',
                'questions': [
                    "What is the current wheat price per quintal?",
                    "Best time to sell tomatoes for profit?",
                    "How to get MSP for my paddy crop?",
                ]
            },
            {
                'name': 'Crop Guide',
                'icon': '🌱',
                'questions': [
                    "What fertilizer is best during flowering stage?",
                    "How to improve soil health for better yield?",
                    "What is the recommended irrigation for wheat?",
                ]
            },
            {
                'name': 'Pest Solutions',
                'icon': '🐛',
                'questions': [
                    "How to control aphids in mustard crop?",
                    "What is the treatment for leaf spot in tomato?",
                    "How to prevent fruit borer in brinjal?",
                ]
            }
        ]
    })


# ── LIVE MARKET PRICES from data.gov.in ──────────────────
DATAGOV_API_KEY = '579b464db66ec23bdd0000014d9fdfa6dbf34dfc731474736312f8b6'
DATAGOV_RESOURCE = '35985678-0d79-46b4-9ed6-6f13308a1d24'
_market_cache = {'data': None, 'ts': 0}  # Cache for 30 minutes

# MSP rates 2024-25 (Government of India gazette) — used as fallback & reference
MSP_DATA = {
    'Wheat':       {'msp': 2275, 'icon': '🌾'},
    'Rice':        {'msp': 2300, 'icon': '🍚'},
    'Mustard':     {'msp': 5650, 'icon': '🌻'},
    'Cotton':      {'msp': 6620, 'icon': '🏵️'},
    'Soyabean':    {'msp': 4600, 'icon': '🫘'},
    'Maize':       {'msp': 2090, 'icon': '🌽'},
    'Gram':        {'msp': 5440, 'icon': '🫘'},
    'Onion':       {'msp': None, 'icon': '🧅'},
    'Tomato':      {'msp': None, 'icon': '🍅'},
    'Potato':      {'msp': None, 'icon': '🥔'},
}

COMMODITIES_TO_FETCH = ['Wheat', 'Rice', 'Tomato', 'Onion', 'Cotton', 'Soyabean', 'Maize', 'Gram', 'Potato', 'Mustard']

def _fetch_live_prices():
    """Fetch live mandi prices from data.gov.in"""
    import urllib.request, urllib.parse
    results = []
    for commodity in COMMODITIES_TO_FETCH:
        try:
            params = urllib.parse.urlencode({
                'api-key': DATAGOV_API_KEY,
                'format': 'json',
                'limit': 5,
                'filters[Commodity]': commodity,
                'sort[Arrival_Date]': 'desc'
            })
            url = f'https://api.data.gov.in/resource/{DATAGOV_RESOURCE}?{params}'
            req = urllib.request.Request(url, headers={'User-Agent': 'KrishiMindAI/1.0'})
            r = urllib.request.urlopen(req, timeout=10)
            data = json.loads(r.read())

            records = data.get('records', [])
            if not records:
                continue

            # Compute average modal price from latest records
            modal_prices = [int(rec.get('Modal_Price', 0)) for rec in records if rec.get('Modal_Price')]
            min_prices = [int(rec.get('Min_Price', 0)) for rec in records if rec.get('Min_Price')]
            max_prices = [int(rec.get('Max_Price', 0)) for rec in records if rec.get('Max_Price')]

            if not modal_prices:
                continue

            avg_modal = round(sum(modal_prices) / len(modal_prices))
            avg_min = round(sum(min_prices) / len(min_prices)) if min_prices else avg_modal
            avg_max = round(sum(max_prices) / len(max_prices)) if max_prices else avg_modal

            # Use the most recent record for mandi name
            latest = records[0]
            mandi_name = f"{latest.get('Market', 'Unknown')}, {latest.get('State', '')}"
            arrival_date = latest.get('Arrival_Date', '')

            msp_info = MSP_DATA.get(commodity, {})
            results.append({
                'crop': commodity,
                'icon': msp_info.get('icon', '🌱'),
                'mandi': mandi_name,
                'unit': 'qt',
                'price': avg_modal,
                'min_price': avg_min,
                'max_price': avg_max,
                'msp': msp_info.get('msp'),
                'arrival_date': arrival_date,
                'source': 'data.gov.in (Live)',
                'history': modal_prices + [avg_modal] * (7 - len(modal_prices))  # pad to 7
            })
        except Exception as e:
            print(f'[Market] Failed to fetch {commodity}: {e}')
            continue
    return results


def _fallback_msp_prices():
    """Fallback to hardcoded MSP data when API is unavailable"""
    now = datetime.now()
    day_seed = int(now.strftime('%Y%m%d'))
    fallback = [
        {"crop": "Wheat", "icon": "🌾", "mandi": "Azadpur, Delhi", "msp": 2275, "avg": 2450},
        {"crop": "Rice", "icon": "🍚", "mandi": "Karnal, Haryana", "msp": 2300, "avg": 2380},
        {"crop": "Mustard", "icon": "🌻", "mandi": "Jaipur, Rajasthan", "msp": 5650, "avg": 5200},
        {"crop": "Cotton", "icon": "🏵️", "mandi": "Rajkot, Gujarat", "msp": 6620, "avg": 6350},
        {"crop": "Soyabean", "icon": "🫘", "mandi": "Indore, MP", "msp": 4600, "avg": 4380},
        {"crop": "Maize", "icon": "🌽", "mandi": "Davangere, Karnataka", "msp": 2090, "avg": 2150},
        {"crop": "Gram", "icon": "🫘", "mandi": "Indore, MP", "msp": 5440, "avg": 5300},
        {"crop": "Onion", "icon": "🧅", "mandi": "Lasalgaon, Maharashtra", "msp": None, "avg": 1500},
        {"crop": "Tomato", "icon": "🍅", "mandi": "Kolar, Karnataka", "msp": None, "avg": 1100},
        {"crop": "Potato", "icon": "🥔", "mandi": "Agra, UP", "msp": None, "avg": 820},
    ]
    prices = []
    for i, c in enumerate(fallback):
        seed = (day_seed * 31 + i * 7) % 100
        change = round((seed - 50) / 15, 1)
        base = c['msp'] if c['msp'] else c['avg']
        history = [round(base * (1 + ((day_seed - 6 + d) * 31 + i * 13) % 100 - 50) / 15000) + base for d in range(7)]
        prices.append({
            'crop': c['crop'], 'icon': c['icon'], 'mandi': c['mandi'],
            'unit': 'qt', 'price': c['avg'], 'msp': c['msp'],
            'change': change, 'source': 'MSP 2024-25 (Offline)',
            'history': history
        })
    return prices


@app.route('/api/market-prices', methods=['GET'])
def market_prices():
    """Live mandi prices from data.gov.in + Govt MSP for reference.
       Cached for 30 minutes. Falls back to MSP data if API fails.
    """
    now = datetime.now()

    # Check cache (30 min = 1800 sec)
    if _market_cache['data'] and (time.time() - _market_cache['ts']) < 1800:
        return jsonify(_market_cache['data'])

    # Try live API
    live_prices = _fetch_live_prices()

    if live_prices and len(live_prices) >= 3:
        # Compute change as (price - MSP) / MSP % for MSP crops
        for p in live_prices:
            if p['msp']:
                p['change'] = round((p['price'] - p['msp']) / p['msp'] * 100, 1)
            else:
                # For non-MSP crops, use min vs modal as proxy
                p['change'] = round((p['price'] - p.get('min_price', p['price'])) / max(p['price'], 1) * 100, 1)

        result = {
            'prices': live_prices,
            'source': 'data.gov.in — Daily Price of Various Commodities (Govt. of India)',
            'updated': now.isoformat(),
            'live': True,
            'note': 'Live prices from registered mandis across India. MSP = Minimum Support Price (Govt. guaranteed).'
        }
    else:
        # Fallback to hardcoded MSP
        result = {
            'prices': _fallback_msp_prices(),
            'source': 'Ministry of Agriculture & Farmers Welfare, Govt. of India (MSP 2024-25)',
            'updated': now.isoformat(),
            'live': False,
            'note': 'MSP = Minimum Support Price (Govt. guaranteed). Live API unavailable, showing reference rates.'
        }

    _market_cache['data'] = result
    _market_cache['ts'] = time.time()
    return jsonify(result)


@app.route('/api/crop-guide', methods=['GET'])
def crop_guide():
    """Crop guide data"""
    return jsonify({'crops': [
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
    ]})


@app.route('/api/pest-solutions', methods=['GET'])
def pest_solutions():
    """Pest and disease solutions"""
    return jsonify({'pests': [
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
    ]})


@app.route('/api/schemes', methods=['GET'])
def schemes():
    """Government schemes data"""
    return jsonify({'schemes': [
        {"name": "PM-KISAN", "icon": "💸", "desc": "₹6,000/year income support for farmers"},
        {"name": "PM Fasal Bima Yojana", "icon": "🛡️", "desc": "Crop insurance against natural calamities"},
        {"name": "Soil Health Card", "icon": "🧪", "desc": "Free soil testing and nutrient recommendations"},
        {"name": "Kisan Credit Card (KCC)", "icon": "💳", "desc": "Low interest loans for agricultural needs"},
        {"name": "e-NAM", "icon": "📱", "desc": "National Agriculture Market for better prices"},
        {"name": "Paramparagat Krishi Vikas", "icon": "🍂", "desc": "Promotion of organic farming"},
    ]})


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

if __name__ == '__main__':
    print("=" * 50)
    print("  KrishiMind AI — API Server")
    print("=" * 50)

    # Pre-load services
    get_faiss_searcher()
    get_watsonx_service()

    print("\n  Dashboard: http://localhost:5000/dashboard/")
    print("  API:       http://localhost:5000/api/health")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5000, debug=False)
