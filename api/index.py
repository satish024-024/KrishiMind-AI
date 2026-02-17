from api_server import app

# Vercel needs the app explicitly exposed as 'app'
# This file serves as the entry point for Vercel functions (AWS Lambda under the hood)
# It maps /api/index.py to the Flask app

# Note: Vercel limitations (250MB size) might block heavy ML libraries
# If deployment fails, we might need a requirements.txt without 'sentence-transformers'
