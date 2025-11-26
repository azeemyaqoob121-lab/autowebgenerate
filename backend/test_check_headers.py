"""Check response headers to see why decompression fails"""
import requests

url = "https://www.ccelectricalservices.co.uk"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
}

response = requests.get(url, headers=headers, timeout=15)

print(f"Status: {response.status_code}")
print(f"Response headers:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

print(f"\nresponse.encoding: {response.encoding}")
print(f"len(response.content): {len(response.content)}")
print(f"len(response.text): {len(response.text)}")

print(f"\nFirst 100 bytes of response.content:")
print(response.content[:100])

print(f"\nFirst 200 chars of response.text:")
try:
    print(response.text[:200])
except:
    # If Unicode error, show ASCII only
    ascii_text = ''.join(c if ord(c) < 128 else '?' for c in response.text[:200])
    print(ascii_text)
