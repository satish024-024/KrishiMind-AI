
import urllib.request, urllib.parse, json

DATAGOV_API_KEY = '579b464db66ec23bdd0000014d9fdfa6dbf34dfc731474736312f8b6'
DATAGOV_RESOURCE = '35985678-0d79-46b4-9ed6-6f13308a1d24'

def test_historical(commodity, limit=10):
    params = urllib.parse.urlencode({
        'api-key': DATAGOV_API_KEY,
        'format': 'json',
        'limit': limit,
        'filters[Commodity]': commodity,
        'sort[Arrival_Date]': 'desc'
    })
    url = f'https://api.data.gov.in/resource/{DATAGOV_RESOURCE}?{params}'
    print(f"Fetching from: {url}")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'KrishiMindAI/1.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            records = data.get('records', [])
            print(f"Fetched {len(records)} records for {commodity}")
            if records:
                for i, rec in enumerate(records[:3]):
                    print(f"Record {i}: Date={rec.get('Arrival_Date')}, State={rec.get('State')}, Mandi={rec.get('Market')}, Price={rec.get('Modal_Price')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_historical('Wheat', 5)
