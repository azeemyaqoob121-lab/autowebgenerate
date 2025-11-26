# Quick Start Guide - After Scraping Fix

## What Was Fixed

✅ **Brotli compression issue** - Scraper now correctly decompresses HTML
✅ **Cleaned 6 corrupted businesses** from database
✅ **HTML validation** - Now less strict, avoids false positives
✅ **Template generation** - Ready to work with Gemini/ChatGPT

## How to Test the Complete Flow

### Step 1: Restart Backend (IMPORTANT!)

```bash
# Stop current backend if running (Ctrl+C)
cd backend
uvicorn app.main:app --reload --port 8000
```

**Why?** The backend needs to reload the fixed `website_scraper.py` code.

### Step 2: Restart Frontend

```bash
# In a new terminal
cd frontend
npm run dev
```

### Step 3: Test the Flow

1. **Search for a new business:**
   - Location: "London"
   - Category: "electrician"
   - Click "Discover"

2. **Watch the magic happen:**
   - ✅ Business discovered via Google Places API
   - ✅ Website scraped (now with proper decompression!)
   - ✅ Data saved to database correctly
   - ✅ Auto-evaluation with Lighthouse
   - ✅ AI template generation starts automatically

3. **View the template:**
   - Click on the business card
   - Template preview should load **correctly** (no more corruption!)
   - You can open in new tab to see full preview

### Step 4: Test Regeneration

If you want to regenerate with Gemini specifically:

1. Open any business card
2. Click "Regenerate" button
3. Template will be regenerated with fresh scraped data

## Checking Configuration

Make sure Gemini is enabled in your `.env`:

```env
# In backend/.env
USE_GEMINI_GENERATION=True  # or False for ChatGPT
GEMINI_MODEL=gemini-1.5-pro  # or gemini-1.5-flash
GEMINI_API_KEY=your_key_here
```

## What Happens Now

### On Search (Discover):
1. Google Places API finds real businesses
2. **Scraper fetches HTML (now works correctly!)**
3. Data saved to database with proper HTML
4. Lighthouse evaluates website
5. If score < 70 → Auto-generates template

### On Template View:
1. Frontend checks for corruption
2. **No more corruption detected!**
3. Template displays in iframe
4. User can view, regenerate, or open in new tab

## Troubleshooting

### Issue: Still seeing corrupted templates

**Solution:** Run cleanup again:
```bash
cd backend
python cleanup_corrupted_templates.py
```

Then restart backend and regenerate templates.

### Issue: Templates not generating

**Check:**
1. Is backend running? (`http://localhost:8000/docs`)
2. Are API keys configured? (OpenAI or Gemini)
3. Check backend logs for errors

### Issue: Frontend not loading

**Check:**
1. Is frontend running on port 3000?
2. Is backend running on port 8000?
3. Check browser console for CORS errors

## Expected Results

### Before Fix:
- ❌ Scraped data: Binary garbage
- ❌ Templates: Not generated or corrupted
- ❌ Preview: Shows "Corrupted Template Data Detected"

### After Fix:
- ✅ Scraped data: Valid HTML (600KB+)
- ✅ Templates: Generated with ChatGPT/Gemini
- ✅ Preview: Beautiful modern website displayed correctly

## Files Modified

1. `backend/app/services/website_scraper.py` - Fixed brotli compression issue
2. `backend/app/services/template_generator_premium.py` - Fixed corruption detection
3. `backend/cleanup_corrupted_templates.py` - Cleanup script (run once)

## Next Steps

1. ✅ **Restart backend** (load fixed code)
2. ✅ **Search for businesses** (test scraping)
3. ✅ **View templates** (verify display)
4. ✅ **Test regeneration** (check Gemini)

Everything should now work correctly! 🚀
