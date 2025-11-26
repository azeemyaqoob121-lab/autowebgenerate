"""
Direct scraping test to see what HTML we're actually getting
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.ccelectricalservices.co.uk"

print(f"Fetching: {url}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=15)
print(f"Status: {response.status_code}")
print(f"Encoding: {response.encoding}")
print(f"Content length: {len(response.content)} bytes")

# Try to decode
try:
    encoding = response.encoding if response.encoding else 'utf-8'
    html = response.content.decode(encoding, errors='ignore')
except:
    html = response.content.decode('utf-8', errors='replace')

# Remove NULL bytes
html = html.replace('\x00', '')

print(f"Decoded HTML length: {len(html)} bytes")
print(f"\nFirst 500 characters:")
print("=" * 80)
print(html[:500])
print("=" * 80)

# Check for HTML tags
html_lower = html.lower()
print(f"\nHas <!doctype: {('<!doctype' in html_lower)}")
print(f"Has <html: {('<html' in html_lower)}")
print(f"Has <body: {('<body' in html_lower)}")
print(f"Has <div: {('<div' in html_lower)}")

# Try BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
print(f"\nBeautifulSoup parsed successfully")
print(f"Found {len(soup.find_all('div'))} div tags")
print(f"Found {len(soup.find_all('img'))} img tags")
print(f"Found {len(soup.find_all(['h1', 'h2', 'h3']))} heading tags")

# Check for printable characters in first 100
first_100 = html[:100].strip()
printable_count = sum(1 for c in first_100 if c.isprintable() or c in ['\n', '\r', '\t'])
print(f"\nFirst 100 chars printable: {printable_count}/{len(first_100)} ({printable_count/len(first_100)*100:.1f}%)")
