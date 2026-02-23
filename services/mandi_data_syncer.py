
import json
import time
import os
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

# Major agricultural states to fetch specific history for
MAJOR_STATES = [
    'Maharashtra', 'Punjab', 'Uttar Pradesh', 'Rajasthan', 
    'Madhya Pradesh', 'Gujarat', 'Haryana', 'Karnataka', 'West Bengal',
    'Andhra Pradesh'
]

# API Configuration (same as in api_server.py)
DATAGOV_API_KEY = '579b464db66ec23bdd0000014d9fdfa6dbf34dfc731474736312f8b6'
DATAGOV_RESOURCE = '35985678-0d79-46b4-9ed6-6f13308a1d24'

# Files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(BASE_DIR, 'data', 'original_crop_history.json')
CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'crop_price_history.json') # Source for MSP icons

COMMODITIES = ['Wheat', 'Rice', 'Tomato', 'Onion', 'Cotton', 'Soyabean', 'Maize', 'Gram', 'Potato', 'Mustard']

def fetch_historical_data(commodity, days=180):
    """
    Fetch historical records from data.gov.in for a commodity.
    Limit 1000 records to cover historical depth.
    """
    limit = 1000 
    params = urllib.parse.urlencode({
        'api-key': DATAGOV_API_KEY,
        'format': 'json',
        'limit': limit,
        'filters[Commodity]': commodity,
        'sort[Arrival_Date]': 'desc'
    })
    url = f'https://api.data.gov.in/resource/{DATAGOV_RESOURCE}?{params}'
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'KrishiMindAI/1.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            return data.get('records', [])
    except Exception as e:
        print(f"Error fetching {commodity}: {e}")
        return []

def aggregate_by_date(records):
    """
    Groups records by date and returns a list of {date, price}
    Price is the average of modal prices for that day.
    """
    date_map = {}
    for rec in records:
        raw_date = rec.get('Arrival_Date')
        try:
            # Date format usually DD/MM/YYYY
            dt = datetime.strptime(raw_date, '%d/%m/%Y')
            iso_date = dt.strftime('%Y-%m-%d')
            price = int(rec.get('Modal_Price', 0))
            
            if iso_date not in date_map:
                date_map[iso_date] = []
            date_map[iso_date].append(price)
        except:
            continue
            
    # Sort dates and calculate averages
    sorted_dates = sorted(date_map.keys())
    history = []
    for d in sorted_dates:
        prices = date_map[d]
        avg_price = sum(prices) // len(prices)
        history.append({'date': d, 'price': avg_price})
    
    return history



# Corrected mapping to match data.gov.in Commodity names
COMMODITY_MAP = {
    'Wheat': 'Wheat',
    'Rice': 'Rice',
    'Tomato': 'Tomato',
    'Onion': 'Onion',
    'Cotton': 'Cotton',
    'Soyabean': 'Soyabean',
    'Maize': 'Maize',
    'Gram': 'Bengal Gram(Gram)(Whole)',
    'Potato': 'Potato',
    'Mustard': 'Mustard'
}

# Sanity price bounds per commodity (real-world plausible ranges, INR/qt)
# Prices outside these bounds are likely data errors
PRICE_BOUNDS = {
    'Wheat':    (1500, 4000),
    'Rice':     (1800, 5000),
    'Tomato':   (200,  8000),
    'Onion':    (300,  6000),
    'Cotton':   (5000, 12000),
    'Soyabean': (3500, 7000),
    'Maize':    (1000, 3500),
    'Gram':     (3500, 8000),
    'Potato':   (300,  4000),
    'Mustard':  (4000, 9000),
}

ICONS = {
    'Wheat': '🌾', 'Rice': '🍚', 'Mustard': '🌻', 'Cotton': '🏵️',
    'Soyabean': '🫘', 'Maize': '🌽', 'Gram': '🫘', 'Onion': '🧅',
    'Tomato': '🍅', 'Potato': '🥔'
}




def fetch_historical_data(commodity_name, total_records=5000):
    """
    Fetch historical records from data.gov.in using pagination.
    Fetches 1000 records at a time until total_records is reached.
    """
    ogd_name = COMMODITY_MAP.get(commodity_name, commodity_name)
    all_records = []
    limit = 1000
    
    for offset in range(0, total_records, limit):
        params = urllib.parse.urlencode({
            'api-key': DATAGOV_API_KEY,
            'format': 'json',
            'limit': limit,
            'offset': offset,
            'filters[Commodity]': ogd_name,
            'sort[Arrival_Date]': 'desc'
        })
        url = f'https://api.data.gov.in/resource/{DATAGOV_RESOURCE}?{params}'
        
        print(f"    Fetching {commodity_name} batch (offset {offset})...")
        retries = 2
        batch_records = []
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'KrishiMindAI/1.0'})
                with urllib.request.urlopen(req, timeout=40) as r:
                    data = json.loads(r.read())
                    batch_records = data.get('records', [])
                    break
            except Exception as e:
                print(f"      Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        
        if not batch_records:
            break
            
        all_records.extend(batch_records)
        if len(batch_records) < limit:
            break
            
        time.sleep(0.5) # Slight delay between batches
        
    return all_records

def aggregate_by_date(records, commodity_name=None, filter_state=None):
    """
    Groups records by date and returns a list of {date, price}
    Price is the median of modal prices for that day.
    If filter_state is provided, only uses records from that state.
    """
    bounds = PRICE_BOUNDS.get(commodity_name, (100, 100000)) if commodity_name else (100, 100000)
    date_map = {}
    
    for rec in records:
        if filter_state and rec.get('State') != filter_state:
            continue
            
        raw_date = rec.get('Arrival_Date')
        try:
            dt = datetime.strptime(raw_date, '%d/%m/%Y')
            iso_date = dt.strftime('%Y-%m-%d')
            price_str = rec.get('Modal_Price', '0')
            if not price_str: continue
            price = int(float(price_str))
            
            if price < bounds[0] or price > bounds[1]:
                continue
                
            if iso_date not in date_map:
                date_map[iso_date] = []
            date_map[iso_date].append(price)
        except:
            continue

    sorted_dates = sorted(date_map.keys())
    history = []
    for d in sorted_dates:
        prices = sorted(date_map[d])
        if not prices: continue
        n = len(prices)
        if n >= 4:
            q1 = prices[n // 4]
            q3 = prices[(3 * n) // 4]
            iqr = q3 - q1
            prices = [p for p in prices if (q1 - 1.5 * iqr) <= p <= (q3 + 1.5 * iqr)]
        
        if not prices: continue
        n = len(prices)
        median_price = prices[n // 2] if n % 2 == 1 else (prices[n // 2 - 1] + prices[n // 2]) // 2
        history.append({'date': d, 'price': median_price})

    return history

def sync_all():
    """Main sync loop for all crops."""
    print(f"[{datetime.now()}] Starting Mandi Data Sync (Original Data)...")
    
    # Load config for icons/msp
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        config = {'crops': {}}
        
    output_data = {
        'source': 'data.gov.in',
        'last_updated': datetime.now().isoformat(),
        'crops': {}
    }
    
    for commodity in COMMODITY_MAP.keys():
        print(f"  Fetching history for {commodity}...")
        records = fetch_historical_data(commodity)
        
        # 1. National History
        national_history = aggregate_by_date(records, commodity_name=commodity)
        
        # 2. State-wise History
        state_histories = {}
        for state in MAJOR_STATES:
            s_history = aggregate_by_date(records, commodity_name=commodity, filter_state=state)
            if s_history:
                state_histories[state] = s_history
        
        if national_history:
            crop_meta = config.get('crops', {}).get(commodity, {})
            output_data['crops'][commodity] = {
                'icon': ICONS.get(commodity, '📦'),
                'msp': crop_meta.get('msp', 2425 if commodity == 'Wheat' else 0),
                'history': national_history,
                'states': state_histories,
                'count': len(national_history)
            }
            print(f"    Saved {len(national_history)} national points and {len(state_histories)} state histories.")
        else:
            print(f"    No records found for {commodity}.")
            
        time.sleep(1) # Rate limit respect
        
    # Ensure dir exists
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"[{datetime.now()}] Sync complete. Saved to {HISTORY_FILE}")

if __name__ == "__main__":
    sync_all()
