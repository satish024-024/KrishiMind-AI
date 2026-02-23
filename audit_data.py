import json

with open('data/original_crop_history.json', 'r') as f:
    data = json.load(f)

last_sync = data.get('last_updated', 'unknown')
print('=== REAL DATA AUDIT ===')
print('Last synced from data.gov.in:', last_sync)
print()

for crop, info in data.get('crops', {}).items():
    history = info.get('history', [])
    if history:
        first = history[0]['date']
        last = history[-1]['date']
        prices = [h['price'] for h in history]
        print(crop + ': ' + str(len(history)) + ' real records | ' + first + ' to ' + last +
              ' | range Rs ' + str(min(prices)) + '-' + str(max(prices)) + ' | latest=Rs ' + str(prices[-1]))
    else:
        print(crop + ': NO REAL DATA -- will use synthetic fallback')
