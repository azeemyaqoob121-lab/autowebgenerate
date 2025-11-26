# 🚀 Gemini AI Integration Guide

## ✅ What's Been Set Up

1. **Gemini SDK Installed** ✅
2. **Configuration Added** ✅
3. **Gemini HTML Generator Created** ✅
4. **Template Generator Updated** ✅

---

## 🔑 How to Get Your Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Click **"Create API Key"**
3. Copy your API key

---

## ⚙️ How to Enable Gemini

### Option 1: Use .env File (Recommended)

Edit your `backend/.env` file and add:

```env
# Gemini AI Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here
USE_GEMINI_GENERATION=true
GEMINI_MODEL=gemini-1.5-pro
```

### Option 2: Set Environment Variables

Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="your_gemini_api_key"
$env:USE_GEMINI_GENERATION="true"
$env:GEMINI_MODEL="gemini-1.5-pro"
```

---

## 🎯 Available Gemini Models

### **gemini-1.5-pro** (Recommended)
- **Best quality** for complex HTML generation
- Supports 8,192 output tokens
- Cost: ~$0.00125 per 1K tokens (cheaper than GPT-4!)

### **gemini-1.5-flash** (Faster)
- **Faster** generation
- Good quality, less cost
- Best for simple templates

---

## 🔄 Switching Between ChatGPT and Gemini

### Use Gemini:
```env
USE_GEMINI_GENERATION=true
```

### Use ChatGPT:
```env
USE_GEMINI_GENERATION=false
```

Or remove the line completely (defaults to ChatGPT)

---

## 📊 What Gemini Does

Your Gemini integration does EXACTLY what ChatGPT does:

1. **Scrapes business website** (logo, images, videos, content, colors, fonts)
2. **Generates 3 HTML variants** in parallel with different styles:
   - Ultra-modern gradient
   - Professional glassmorphism
   - Creative animation-heavy
3. **AI validates each variant** (scores 0-100)
4. **Selects best variant**
5. **Refines with AI** to make it PERFECT
6. **Returns beautiful modern website**

---

## 💰 Cost Comparison

| AI Engine | Cost per 1K tokens | Quality |
|-----------|-------------------|---------|
| **Gemini 1.5 Pro** | $0.00125 | Excellent ⭐⭐⭐⭐⭐ |
| GPT-4 Turbo | $0.01 | Excellent ⭐⭐⭐⭐⭐ |

**Gemini is ~8x cheaper than GPT-4!** 🎉

---

## 🧪 Testing Gemini

### 1. Start your backend:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 2. Generate a template via API:
```bash
POST http://localhost:8000/api/businesses/{business_id}/templates/generate
```

### 3. Check logs:
You'll see:
```
[GEMINI] Generating brand-new modern HTML using GEMINI MAXIMUM QUALITY mode
[GEMINI] Model: gemini-1.5-pro
[STAGE 1] Generating 3 variants in parallel...
[STAGE 2] Using AI to validate each variant...
[STAGE 3] ✅ Best variant: ultra-modern-gradient (score: 95/100)
[GEMINI SUCCESS] Generated PERFECT quality website!
```

---

## ❓ Troubleshooting

### Error: "Gemini API key is required"
**Solution:** Make sure you've set `GEMINI_API_KEY` in your .env file

### Error: "google.generativeai module not found"
**Solution:** Run: `pip install google-generativeai`

### Templates still using ChatGPT
**Solution:** Make sure `USE_GEMINI_GENERATION=true` in .env file

---

## 🎨 What Gets Scraped and Used

Gemini uses ALL scraped data to create beautiful websites:

### From Business Website:
- ✅ Logo (preserves your brand)
- ✅ All images
- ✅ All videos
- ✅ Brand colors (exact hex codes)
- ✅ Fonts
- ✅ Content (headlines, about, services)
- ✅ Navigation menu
- ✅ Testimonials
- ✅ Contact info
- ✅ Page structure

### What Gemini Generates:
- ✅ Modern HTML5 website
- ✅ Tailwind CSS styling
- ✅ Smooth animations
- ✅ Mobile responsive
- ✅ Glassmorphism effects
- ✅ Gradient backgrounds
- ✅ Perfect alignment
- ✅ Professional typography

---

## 🚀 Next Steps

1. **Get Gemini API key** from https://makersuite.google.com/app/apikey
2. **Add to .env file**:
   ```env
   GEMINI_API_KEY=your_key_here
   USE_GEMINI_GENERATION=true
   ```
3. **Restart your backend server**
4. **Generate templates** - they'll now use Gemini!

---

## 📝 File Changes Made

1. `backend/app/config.py` - Added Gemini config
2. `backend/app/services/gemini_html_generator.py` - NEW file (Gemini generator)
3. `backend/app/services/template_generator_premium.py` - Updated to support Gemini
4. `backend/.env` - Added Gemini config (you need to add your key)

---

## 🎉 That's It!

You now have **BOTH** ChatGPT and Gemini integrated!

Switch between them anytime using the `USE_GEMINI_GENERATION` flag.

**Enjoy generating beautiful websites with Gemini!** 🚀
