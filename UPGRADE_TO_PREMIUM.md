# Upgrade to Premium Template Generator

**Current Status:** Your system is working with the BASIC template generator (copies old website designs).
**Goal:** Upgrade to PREMIUM generator (creates brand new $50,000+ quality designs).

---

## Why You're Still Seeing Old Website Copies

The premium template generator is installed but NOT active because it needs the `aiohttp` package.
Your system is currently using the **old/basic generator** which copies existing website designs.

---

## Simple 3-Step Upgrade Process

### Step 1: Install aiohttp Package

Open PowerShell or Command Prompt and run this command:

```bash
venv\Scripts\pip.exe install aiohttp
```

**Verify installation:**
```bash
venv\Scripts\python.exe -c "import aiohttp; print('aiohttp installed successfully!')"
```

### Step 2: Activate Premium Generator

Open these two files and change ONE line in each:

#### File 1: `backend/app/routes/businesses.py` (Line 22)

**CHANGE THIS:**
```python
from app.services.template_generator import generate_templates_for_business
```

**TO THIS:**
```python
from app.services.template_generator_premium import generate_templates_for_business
```

#### File 2: `backend/app/routes/templates.py` (Lines 16-20)

**CHANGE THIS:**
```python
from app.services.template_generator import (
    generate_templates_for_business,
    delete_existing_templates,
    TemplateGenerationError
)
```

**TO THIS:**
```python
from app.services.template_generator_premium import (
    generate_templates_for_business,
    TemplateGenerationError
)
from app.services.template_generator import delete_existing_templates
```

### Step 3: Restart Backend Server

1. **Kill existing backend** (Press Ctrl+C in the backend terminal OR run):
   ```bash
   taskkill /F /IM python.exe
   ```

2. **Start backend fresh**:
   ```bash
   cd backend
   ..\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Verify it started** - You should see:
   ```
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

---

## What You'll Get After Upgrade

### BEFORE (Current - Basic Generator):
- Copies existing website design
- Basic HTML/CSS
- Generic placeholder images
- Simple layouts
- Score improvements only

### AFTER (Premium Generator):
- **Brand new modern designs** (not copies!)
- Glassmorphism navigation with blur effects
- 10+ smooth animations (fadeInUp, float, typing, slideIn, bounce)
- Hero background videos (muted, autoplay, loop)
- 15+ business-specific images from Unsplash
- Mobile-first responsive design
- Scroll-triggered reveal animations
- Business-niche specialization (restaurant, plumber, gym, etc.)
- GPT-4 enhanced copywriting
- Schema.org SEO markup
- **$50,000+ quality websites!**

---

## Optional: Get Real Images & Videos

The premium generator works WITHOUT API keys (uses placeholder images), but for best results:

### Unsplash API (FREE - 50 requests/hour)
1. Go to: https://unsplash.com/developers
2. Create account
3. Create application
4. Copy Access Key

### Pexels API (FREE - 200 requests/hour)
1. Go to: https://www.pexels.com/api/
2. Create account
3. Copy API Key

### Add to `.env` file:
```bash
UNSPLASH_API_KEY=your_key_here
PEXELS_API_KEY=your_key_here
PREMIUM_TEMPLATE_MODE=true
DEFAULT_IMAGE_COUNT=15
ENABLE_VIDEO_BACKGROUNDS=true
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'aiohttp'"
**Solution:** Run Step 1 again to install aiohttp

### Issue: Backend won't start after changes
**Solution:**
1. Check for typos in the import statements
2. Make sure aiohttp is installed
3. Kill all Python processes and restart

### Issue: Still seeing old website designs
**Solution:**
1. Verify Step 2 changes were saved
2. Restart backend completely (kill and restart)
3. Clear browser cache
4. Try regenerating templates

### Issue: Template generation takes 3+ minutes
**This is NORMAL for premium templates!** They include:
- Website scraping
- GPT-4 content generation
- Image fetching from Unsplash
- Video fetching from Pexels
- Complex HTML/CSS/JS generation

Typical generation time:
- Without APIs: 30-60 seconds
- With APIs: 2-3 minutes

---

## Quick Test

After upgrading, test with a new business:

1. Discover a restaurant in London
2. System will auto-generate template
3. Check the generated template - you should see:
   - Modern glassmorphism design
   - Smooth animations
   - High-quality food images
   - Hero background video (or placeholder)
   - Mobile-responsive layout
   - NO copying of old website!

---

## Summary

**What to do RIGHT NOW:**

1. Run: `venv\Scripts\pip.exe install aiohttp`
2. Edit 2 files (change import statements)
3. Restart backend
4. Generate a template - see the NEW premium designs!

**Time needed:** 5 minutes

**Result:** $50,000+ quality websites that don't copy old designs!

---

**Need Help?**
- Check `PREMIUM_INTEGRATION_STATUS.md` for full details
- Check `docs/IMPLEMENTATION_SUMMARY.md` for technical specs
- All premium template code is in `backend/app/services/template_generator_premium.py`
