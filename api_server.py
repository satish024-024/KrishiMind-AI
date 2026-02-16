"""
KrishiMind AI — REST API Server
Wraps existing FAISS + Gemini services for the new dashboard
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from config import FAISS_INDEX_FILE, METADATA_FILE, GEMINI_API_KEY

DASHBOARD_DIR = Path(__file__).parent / 'dashboard'
from services.faiss_store import FAISSSearcher
from services.query_handler import QueryHandler

app = Flask(__name__)
CORS(app)  # Allow dashboard to call API

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
def serve_dashboard():
    return send_from_directory(str(DASHBOARD_DIR), 'index.html')

@app.route('/dashboard/<path:filename>')
def serve_dashboard_files(filename):
    return send_from_directory(str(DASHBOARD_DIR), filename)


# ── API Routes ───────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'faiss_ready': get_faiss_searcher() is not None,
        'ai_ready': get_watsonx_service() is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/query', methods=['POST'])
def query():
    """Process a farming query"""
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

        # Format response
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

        # If no FAISS results but AI is available, get direct answer
        ai_answer = result.get('online_answer', '')
        if not retrieved and ai and online_mode:
            try:
                prompt = f"A farmer asked: '{user_query}'. Provide a helpful response about agriculture."
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
    """Get popular questions by category"""
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
