"""
KrishiMind AI — REST API Server
Wraps existing FAISS + Gemini services for the new dashboard
"""

import sys
import os
import time
import random
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from config import FAISS_INDEX_FILE, METADATA_FILE, GEMINI_API_KEY
from services.faiss_store import FAISSSearcher
from services.query_handler import QueryHandler

DASHBOARD_DIR = Path(__file__).parent / 'dashboard'

app = Flask(__name__)
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


# ── Serve Dashboard ──────────────────────────────────────

@app.route('/dashboard/')
@app.route('/dashboard')
@app.route('/')
def serve_dashboard():
    return send_from_directory(str(DASHBOARD_DIR), 'index.html')

@app.route('/dashboard/<path:filename>')
def serve_dashboard_files(filename):
    return send_from_directory(str(DASHBOARD_DIR), filename)


# ── API Routes ───────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
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

    start = time.time()

    searcher = get_faiss_searcher()
    if not searcher:
        return jsonify({'error': 'Knowledge base not loaded'}), 503

    ai = get_watsonx_service() if online_mode else None
    handler = QueryHandler(searcher, ai)

    try:
        result = handler.process_query(user_query, top_k=top_k,
                                       online_mode=online_mode and ai is not None)
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
                prompt = f"A farmer asked: '{user_query}'. Provide a helpful, practical response about agriculture in India."
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
            'mode': 'online' if (online_mode and ai) else 'offline'
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


@app.route('/api/market-prices', methods=['GET'])
def market_prices():
    """Realistic Indian agricultural commodity prices"""
    base_prices = [
        {"crop": "Wheat", "icon": "🌾", "mandi": "Azadpur, Delhi", "unit": "qt",
         "base": 2450, "msp": 2275, "change": 3.2},
        {"crop": "Rice (Basmati)", "icon": "🍚", "mandi": "Karnal, Haryana", "unit": "qt",
         "base": 3850, "msp": 2183, "change": 1.8},
        {"crop": "Tomato", "icon": "🍅", "mandi": "Kolar, Karnataka", "unit": "qt",
         "base": 1200, "msp": None, "change": -5.4},
        {"crop": "Onion", "icon": "🧅", "mandi": "Lasalgaon, Maharashtra", "unit": "qt",
         "base": 1680, "msp": None, "change": 2.1},
        {"crop": "Cotton", "icon": "🏵️", "mandi": "Rajkot, Gujarat", "unit": "qt",
         "base": 6200, "msp": 6620, "change": -0.8},
        {"crop": "Soybean", "icon": "🫘", "mandi": "Indore, MP", "unit": "qt",
         "base": 4350, "msp": 4600, "change": 1.5},
        {"crop": "Mustard", "icon": "🌻", "mandi": "Jaipur, Rajasthan", "unit": "qt",
         "base": 5100, "msp": 5650, "change": 0.9},
        {"crop": "Potato", "icon": "🥔", "mandi": "Agra, UP", "unit": "qt",
         "base": 820, "msp": None, "change": -2.3},
        {"crop": "Sugarcane", "icon": "🎋", "mandi": "Muzaffarnagar, UP", "unit": "qt",
         "base": 350, "msp": 315, "change": 0.5},
        {"crop": "Maize", "icon": "🌽", "mandi": "Davangere, Karnataka", "unit": "qt",
         "base": 2090, "msp": 2090, "change": 1.2},
    ]
    # Add slight random variance to simulate real-time
    for p in base_prices:
        variance = random.uniform(-0.5, 0.5)
        p['price'] = round(p['base'] + p['base'] * variance / 100)
        p['change'] = round(p['change'] + random.uniform(-0.3, 0.3), 1)
        # Weekly price history (7 values)
        p['history'] = [round(p['base'] * (1 + random.uniform(-3, 3)/100)) for _ in range(7)]
        p['history'][-1] = p['price']
        del p['base']
    return jsonify({'prices': base_prices, 'updated': datetime.now().isoformat()})


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


if __name__ == '__main__':
    print("=" * 50)
    print("  KrishiMind AI — API Server")
    print("=" * 50)

    get_faiss_searcher()
    get_watsonx_service()

    print("\n  Dashboard: http://localhost:5000/dashboard/")
    print("  API:       http://localhost:5000/api/health")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5000, debug=False)
