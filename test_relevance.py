"""Quick test for relevance filtering"""
from services.faiss_store import FAISSSearcher

s = FAISSSearcher().load()

# Test 1: Relevant query
print("=== RELEVANT QUERY ===")
r1 = s.search("How to control aphids in mustard?")
for x in r1[:3]:
    print(f"  conf={x['confidence']}, q={x['metadata']['question'][:80]}")

# Test 2: Irrelevant query
print("\n=== IRRELEVANT QUERY ===")
r2 = s.search("How to fly a rocket to mars?")
print(f"  Results returned: {len(r2)}")
if r2:
    for x in r2[:2]:
        print(f"  conf={x['confidence']}, dist={x['distance']:.2f}, q={x['metadata']['question'][:80]}")
else:
    print("  (none - correctly filtered out)")

# Test 3: Weather query
print("\n=== WEATHER QUERY ===")
r3 = s.search("What is weather forecast for next 7 days?")
print(f"  Results returned: {len(r3)}")
for x in r3[:3]:
    print(f"  conf={x['confidence']}, q={x['metadata']['question'][:80]}")
