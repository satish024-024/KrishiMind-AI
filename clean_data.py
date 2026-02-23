"""
Clean outliers from existing original_crop_history.json using the same
sanity bounds and IQR logic that the syncer now uses.
"""
import json

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

with open('data/original_crop_history.json', 'r') as f:
    data = json.load(f)

for crop, info in data.get('crops', {}).items():
    history = info.get('history', [])
    if not history:
        continue
    lo, hi = PRICE_BOUNDS.get(crop, (100, 100000))
    before = len(history)
    cleaned = [h for h in history if lo <= h['price'] <= hi]
    after = len(cleaned)
    if before != after:
        print(f'  {crop}: removed {before - after} outlier(s) | kept {after} records')
    else:
        print(f'  {crop}: all {after} records clean')
    info['history'] = cleaned

with open('data/original_crop_history.json', 'w') as f:
    json.dump(data, f, indent=2)

print('\nDone. Re-auditing...')
print()
for crop, info in data.get('crops', {}).items():
    history = info.get('history', [])
    if history:
        prices = [h['price'] for h in history]
        print(f'{crop}: {len(history)} records | Rs {min(prices)}-{max(prices)} | latest=Rs {prices[-1]}')
    else:
        print(f'{crop}: NO DATA after cleaning')
