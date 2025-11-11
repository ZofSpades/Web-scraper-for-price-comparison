# Proxy & User-Agent Rotation - Quick Reference

## 🚀 Quick Start

### No Configuration Needed
```python
# User-agent rotation works automatically!
from scrapers.amazon_scraper import AmazonScraper

scraper = AmazonScraper()
result = scraper.scrape("laptop")
# ✓ User-agent is automatically rotated
```

### With Proxies (Recommended)
```python
from scrapers.base_scraper import BaseScraper

# Configure once at startup
BaseScraper.configure_proxies([
    'http://proxy1.com:8080',
    'http://user:pass@proxy2.com:3128',
])

# All scrapers now use rotation automatically
```

### Using Environment Variables
```bash
# Set in terminal or .env file
export SCRAPER_PROXIES="http://proxy1:8080,http://user:pass@proxy2:3128"

# Run application
python main.py
```

---

## 📊 Check Status

```python
status = BaseScraper.get_rotation_status()
print(f"User Agents: {status['user_agents_count']}")
print(f"Proxies: {status['available_proxies']}/{status['total_proxies']}")
```

---

## 🔧 Common Patterns

### Pattern 1: Basic Usage
```python
from scrapers.amazon_scraper import AmazonScraper

scraper = AmazonScraper()
result = scraper.scrape("laptop")
```

### Pattern 2: Configure Proxies at Startup
```python
# In main.py or config file
from scrapers.base_scraper import BaseScraper

BaseScraper.configure_proxies([
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:3128',
])
```

### Pattern 3: Load from Environment
```python
import os

proxies_str = os.getenv('SCRAPER_PROXIES', '')
if proxies_str:
    proxies = [p.strip() for p in proxies_str.split(',')]
    BaseScraper.configure_proxies(proxies)
```

### Pattern 4: Manual Control (Advanced)
```python
scraper = AmazonScraper()

# Get headers with rotated user-agent
headers = scraper.get_headers()

# Get next proxy
proxy = scraper.get_proxy()

# Make request manually
import requests
response = requests.get(url, headers=headers, proxies=proxy)
```

---

## 🛠️ Proxy Format

```python
# HTTP
'http://host:port'

# HTTPS
'https://host:port'

# With authentication
'http://username:password@host:port'

# Special characters in password? URL encode them:
from urllib.parse import quote
password = quote('p@ssw0rd!')
proxy = f'http://user:{password}@host:port'
```

---

## 🎯 Best Practices

1. **Use Paid Proxies for Production**
   - Free proxies are unreliable
   - Paid services: BrightData, Oxylabs, ScraperAPI

2. **Add Rate Limiting**
   ```python
   import time
   for url in urls:
       result = scraper.scrape(url)
       time.sleep(2)  # 2 second delay
   ```

3. **Monitor Performance**
   ```python
   status = BaseScraper.get_rotation_status()
   if status['available_proxies'] < 2:
       print("⚠ Warning: Low proxy count!")
   ```

4. **Test Proxies First**
   ```bash
   python test_rotation.py
   ```

---

## 🐛 Troubleshooting

### Issue: All requests failing
**Solution:**
```python
# Check proxy status
status = BaseScraper.get_rotation_status()
print(f"Available: {status['available_proxies']}")

# If 0, check proxy credentials
# If > 0, try increasing timeout
scraper.timeout = 30
```

### Issue: Proxy authentication errors
**Solution:**
```python
# Ensure correct format
proxy = 'http://username:password@host:port'

# URL encode special characters
from urllib.parse import quote
proxy = f'http://user:{quote("p@ss")}@host:port'
```

### Issue: Too slow
**Solution:**
- Use datacenter proxies instead of residential
- Increase connection pool
- Check proxy service performance

---

## 📚 Documentation

- **Full Guide:** `PROXY_ROTATION_GUIDE.md`
- **Examples:** `scrapers/rotation_config_example.py`
- **Tests:** `python test_rotation.py`

---

## 🔒 Security

```bash
# ✗ NEVER commit credentials
git status  # Check before commit

# ✓ Use environment variables
export SCRAPER_PROXY="http://user:pass@proxy.com:8080"

# ✓ Use .env file (already in .gitignore)
echo "SCRAPER_PROXY=http://user:pass@proxy.com:8080" > .env
```

---

## 🎓 How It Works

```
Request Flow:
1. scraper.scrape(url) called
2. get_headers() → random user-agent
3. get_proxy() → next available proxy
4. Make request with rotation
5. Success? → mark_proxy_success()
   Failure? → mark_proxy_failure() → retry with new proxy
```

```
Failure Handling:
- Failed proxy marked (1/3 failures)
- Second failure (2/3 failures)
- Third failure (3/3 failures) → disabled for 5 minutes
- After cooldown → proxy re-enabled
```

---

## 📝 Environment Variables Reference

```bash
# Single proxy
SCRAPER_PROXY=http://proxy.com:8080

# Multiple proxies (comma-separated)
SCRAPER_PROXIES=http://proxy1:8080,http://proxy2:3128

# Debug mode
FLASK_DEBUG=True

# Secret key (required for production)
SECRET_KEY=your-secret-key-here
```

---

## 🧪 Testing

```bash
# Run rotation tests
python test_rotation.py

# Expected output:
# ✓ User-Agent Rotation
# ✓ Proxy Rotation
# ✓ Rotation Manager
# ✓ BaseScraper Integration
# 🎉 All tests passed!
```

---

## 📞 Support

- Check `PROXY_ROTATION_GUIDE.md` for detailed documentation
- Run `python test_rotation.py` to verify setup
- Review logs for error messages
- Test proxies independently before adding to pool

---

## 🔄 Update Existing Code

No changes needed! Rotation works automatically:

```python
# Old code (still works)
scraper = AmazonScraper()
result = scraper.scrape("laptop")

# New features work transparently:
# - User-agent is rotated
# - Proxy is used if configured
# - Failures are handled automatically
```

---

**Version:** 1.0  
**Last Updated:** 2025-01-11
