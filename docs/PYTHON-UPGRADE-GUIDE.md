# Python 3.11 64-bit Upgrade Guide

## Why We're Upgrading

**Current**: Python 3.13 32-bit
**Target**: Python 3.11.11 64-bit

**Reasons**:
- Python 3.13 too new - missing pre-built wheels for many packages
- 32-bit Python has limited memory and performance
- 64-bit Python 3.11 is production-ready with all wheels available
- Matches production deployment requirements

---

## Step-by-Step Instructions

### Step 1: Download Python 3.11.11 64-bit

1. **Open this URL in your browser**:
   ```
   https://www.python.org/downloads/release/python-31111/
   ```

2. **Scroll down to "Files" section**

3. **Download**: `Windows installer (64-bit)`
   - File name: `python-3.11.11-amd64.exe`
   - Size: ~25 MB

---

### Step 2: Uninstall Python 3.13 32-bit

1. **Open Windows Settings**
   - Press `Win + I`
   - Or: Control Panel > Programs > Programs and Features

2. **Find "Python 3.13.x (32-bit)"**

3. **Right-click > Uninstall**

4. **Complete uninstallation**
   - This removes the old Python version

---

### Step 3: Install Python 3.11.11 64-bit

1. **Run the installer** (`python-3.11.11-amd64.exe`)

2. **IMPORTANT: Check these boxes**:
   - ✅ **Add Python 3.11 to PATH** (very important!)
   - ✅ Install pip
   - ✅ Install for all users (optional)

3. **Click "Install Now"**

4. **Wait for installation** (~2 minutes)

5. **Click "Close"** when done

---

### Step 4: Verify Python Installation

1. **Open NEW Command Prompt**
   - Press `Win + R`
   - Type `cmd`
   - Press Enter
   - (Important: NEW terminal to pick up PATH changes)

2. **Check Python version**:
   ```cmd
   python --version
   ```
   - Should show: `Python 3.11.11`

3. **Check pip**:
   ```cmd
   pip --version
   ```
   - Should show: `pip 24.x.x from ... (python 3.11)`

---

### Step 5: Navigate to Project and Create Virtual Environment

1. **Navigate to backend directory**:
   ```cmd
   cd "C:\Users\rabia\Documents\project AutoWeb Outreach AI\AutoWeb_Outreach_AI\backend"
   ```

2. **Delete old virtual environment** (if exists):
   ```cmd
   rmdir /s /q venv
   ```
   - Type `Y` if prompted

3. **Create new virtual environment**:
   ```cmd
   python -m venv venv
   ```
   - This creates a fresh Python 3.11 virtual environment

4. **Activate virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```
   - Your prompt should now show `(venv)` at the beginning

---

### Step 6: Install All Dependencies

1. **Upgrade pip** (recommended):
   ```cmd
   python -m pip install --upgrade pip
   ```

2. **Install all requirements**:
   ```cmd
   pip install -r requirements.txt
   ```
   - This time it should work! ✅
   - Estimated time: 2-5 minutes
   - You should see all packages installing successfully

3. **Verify SQLAlchemy installed**:
   ```cmd
   pip show sqlalchemy
   ```
   - Should show: `Version: 2.0.25`

---

### Step 7: Apply Database Migrations

1. **Make sure Docker containers are running**:
   ```cmd
   docker ps
   ```
   - Should show: autoweb-postgres and autoweb-redis

2. **Run migrations**:
   ```cmd
   alembic upgrade head
   ```
   - Should create all database tables

---

### Step 8: Start FastAPI Application

1. **Start the server**:
   ```cmd
   uvicorn app.main:app --reload
   ```
   - Should show: "Application startup complete"
   - Server running at: http://127.0.0.1:8000

2. **Keep this terminal open** (server is running)

---

### Step 9: Test the Application

1. **Open NEW Command Prompt** (keep server running in first one)

2. **Test health endpoint**:
   ```cmd
   curl http://localhost:8000/api/health
   ```
   - Should return JSON with "status": "healthy"

3. **Open in browser**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Root: http://localhost:8000/

---

### Step 10: Run Tests

1. **Navigate to backend** (in second terminal):
   ```cmd
   cd "C:\Users\rabia\Documents\project AutoWeb Outreach AI\AutoWeb_Outreach_AI\backend"
   venv\Scripts\activate
   ```

2. **Run all tests**:
   ```cmd
   pytest tests/ -v
   ```
   - Should pass all tests from Stories 1.1-1.3

3. **Run with coverage**:
   ```cmd
   pytest --cov=app --cov-report=term-missing
   ```

---

## Troubleshooting

### Issue: "python --version" still shows 3.13
**Solution**:
- Close ALL Command Prompt windows
- Open NEW Command Prompt
- PATH needs to refresh

### Issue: "pip: command not found"
**Solution**:
- Reinstall Python 3.11
- Make sure "Add to PATH" was checked

### Issue: "venv\Scripts\activate" doesn't work
**Solution**:
- Try: `venv\Scripts\activate.bat`
- Or use: `call venv\Scripts\activate`

### Issue: Docker containers not running
**Solution**:
```cmd
cd "C:\Users\rabia\Documents\project AutoWeb Outreach AI\AutoWeb_Outreach_AI"
docker-compose up -d
```

### Issue: "alembic: command not found"
**Solution**:
- Virtual environment not activated
- Run: `venv\Scripts\activate`
- Then try again

---

## What You'll See When Successful

### pip install success:
```
Successfully installed SQLAlchemy-2.0.25 alembic-1.13.1 psycopg-3.1.18
pydantic-settings-2.1.0 python-jose-3.3.0 passlib-1.7.4 redis-5.0.1
celery-5.3.6 ...
```

### alembic upgrade success:
```
INFO  [alembic.runtime.migration] Running upgrade -> xxxx, initial_schema
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
```

### uvicorn startup success:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### health check success:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2025-11-01T...",
  "database": "connected"
}
```

---

## After Successful Upgrade

Once everything works, you'll be able to:
- ✅ Run database migrations
- ✅ Start FastAPI application
- ✅ Test all endpoints
- ✅ Run automated tests
- ✅ Continue with Stories 1.4-1.10 development
- ✅ Deploy to production (same Python 3.11 64-bit)

---

## Questions?

If you encounter any issues during the upgrade:
1. Read the Troubleshooting section above
2. Check the error message carefully
3. Let me know which step failed and I'll help debug

---

## Summary

**Time Required**: 15-20 minutes
**Complexity**: Low (just follow steps)
**Risk**: None (can always reinstall)
**Benefit**: All dependencies will work, production-ready setup

**Ready to start? Follow Step 1 above!**
