import urllib.request
import json

try:
    url = 'http://localhost:5000/api/market-prices?state=Andhra%20Pradesh'
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        print(f"Location: {data.get('location')}")
        print(f"Source: {data.get('source')}")
        prices = data.get('prices', [])
        print(f"Found {len(prices)} prices.")
        for p in prices:
            print(f"- {p['crop']}: {p['price']}")
    print("\n--- Predictions ---")
    url_pred = 'http://localhost:5000/api/price-prediction?crop=Rice&state=Andhra%20Pradesh'
    with urllib.request.urlopen(url_pred) as response:
        data = json.loads(response.read().decode())
        print(f"Rice Pred (AP): {data.get('predicted_price')} (Source: {data.get('source')})")

    print("\n--- Advisory ---")
    url_adv = 'http://localhost:5000/api/price-advisory?state=Andhra%20Pradesh'
    with urllib.request.urlopen(url_adv) as response:
        data = json.loads(response.read().decode())
        advs = data.get('advisories', [])
        print(f"Found {len(advs)} advisories for AP.")
        for a in advs[:3]:
            print(f"- {a['crop']}: {a['verdict']} (Source: {a.get('source')})")

except Exception as e:
    print(f"Error: {e}")
