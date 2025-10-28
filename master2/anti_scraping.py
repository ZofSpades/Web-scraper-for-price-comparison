import random
import time
import logging
import requests

logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(message)s')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)"
]

SITE_THROTTLE = {
    "example.com": 2.0,
    "another.com": 1.0
}

MAX_BACKOFF = 60

def fetch_url(url):
    domain = url.split("/")[2]
    delay = SITE_THROTTLE.get(domain, 1.0)
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    
    time.sleep(delay + random.uniform(0.5, 1.5))
    
    backoff = delay
    while True:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 429:
            logging.warning(f"429 Too Many Requests from {domain}. Backing off for {backoff:.1f}s")
            time.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)
            continue
        
        if response.status_code in [403, 503]:
            logging.error(f"Blocked or anti-bot response from {domain}: {response.status_code}")
        
        return response