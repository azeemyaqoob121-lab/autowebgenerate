# AutoWeb Outreach AI - Deployment Guide

Complete guide to deploy your AutoWeb Outreach AI application to production.

---

## Table of Contents

1. [Deployment Options](#deployment-options)
2. [Prerequisites](#prerequisites)
3. [Option 1: Deploy to Railway (Recommended - Easiest)](#option-1-railway)
4. [Option 2: Deploy to Render](#option-2-render)
5. [Option 3: Deploy to AWS](#option-3-aws)
6. [Option 4: Deploy to DigitalOcean](#option-4-digitalocean)
7. [Environment Variables](#environment-variables)
8. [Database Migration](#database-migration)
9. [Domain & SSL Setup](#domain--ssl-setup)
10. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Deployment Options

### Comparison Table

| Platform | Difficulty | Cost | Best For |
|----------|-----------|------|----------|
| **Railway** | ⭐ Easy | $5-20/mo | Quick deployment, startups |
| **Render** | ⭐⭐ Easy | $7-25/mo | Free tier available, simple setup |
| **AWS (EC2)** | ⭐⭐⭐⭐ Hard | $10-50/mo | Enterprise, scalability |
| **DigitalOcean** | ⭐⭐⭐ Medium | $12-30/mo | Good balance of control & ease |
| **Heroku** | ⭐⭐ Easy | $7-25/mo | Simple, but expensive |

**Recommendation:** Start with **Railway** or **Render** for ease of use.

---

## Prerequisites

### 1. Prepare Your Code

```bash
# Ensure all dependencies are in requirements.txt
cd backend
pip freeze > requirements.txt

# Test locally first
python -m uvicorn app.main:app --reload
```

### 2. Create Production Configuration

Create `.env.production` file:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# API Keys
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
UNSPLASH_API_KEY=...
PEXELS_API_KEY=...

# Security
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS (your frontend domain)
CORS_ORIGINS=["https://your-frontend-domain.com"]

# Production settings
ENVIRONMENT=production
DEBUG=False
```

### 3. Prepare Database

Ensure your database schema is ready:

```bash
cd backend
alembic upgrade head
```

---

## Option 1: Railway (Recommended - Easiest)

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### Step 2: Initialize Railway Project

```bash
cd "C:\Users\rabia\Documents\project AutoWeb Outreach AI\AutoWeb_Outreach_AI"
railway init
```

### Step 3: Add PostgreSQL Database

```bash
railway add postgresql
```

Railway will automatically provision a PostgreSQL database and set `DATABASE_URL`.

### Step 4: Deploy Backend

Create `railway.json` in backend folder:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `Procfile` in backend folder:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Deploy:

```bash
cd backend
railway up
```

### Step 5: Set Environment Variables

```bash
railway variables set OPENAI_API_KEY=sk-...
railway variables set GOOGLE_API_KEY=AIza...
railway variables set UNSPLASH_API_KEY=...
railway variables set PEXELS_API_KEY=...
railway variables set SECRET_KEY=your-secret-key
```

### Step 6: Deploy Frontend

```bash
cd frontend
railway up
```

### Step 7: Run Database Migrations

```bash
railway run alembic upgrade head
```

**Done!** Your app is live on Railway.

---

## Option 2: Render

### Step 1: Create Render Account

Go to [render.com](https://render.com) and sign up.

### Step 2: Create PostgreSQL Database

1. Click **New +** → **PostgreSQL**
2. Name: `autoweb-db`
3. Plan: Free or Starter ($7/mo)
4. Click **Create Database**
5. Copy the **Internal Database URL**

### Step 3: Deploy Backend

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name:** `autoweb-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free or Starter ($7/mo)

4. Add Environment Variables:
   ```
   DATABASE_URL=<your-postgres-url>
   OPENAI_API_KEY=sk-...
   GOOGLE_API_KEY=AIza...
   UNSPLASH_API_KEY=...
   PEXELS_API_KEY=...
   SECRET_KEY=your-secret-key
   PYTHON_VERSION=3.11
   ```

5. Click **Create Web Service**

### Step 4: Deploy Frontend

1. Click **New +** → **Static Site**
2. Connect your GitHub repository
3. Configure:
   - **Name:** `autoweb-frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist` or `build`

4. Add Environment Variables:
   ```
   REACT_APP_API_URL=https://autoweb-backend.onrender.com
   ```

5. Click **Create Static Site**

### Step 5: Run Database Migrations

Use Render Shell:

1. Go to your backend service
2. Click **Shell** tab
3. Run:
   ```bash
   alembic upgrade head
   ```

**Done!** Your app is live on Render.

---

## Option 3: AWS (Advanced)

### Architecture

```
[Route 53] → [CloudFront] → [S3 (Frontend)]
                          ↓
[ALB] → [EC2/ECS (Backend)] → [RDS PostgreSQL]
```

### Step 1: Set Up RDS PostgreSQL

1. Go to AWS RDS Console
2. Create Database:
   - Engine: PostgreSQL 15
   - Instance: db.t3.micro (Free Tier) or db.t3.small
   - Storage: 20GB
   - Public Access: No (use VPC)
   - Security Group: Allow port 5432 from backend

3. Note the endpoint URL

### Step 2: Deploy Backend on EC2

**Launch EC2 Instance:**

```bash
# Instance: t2.micro (Free Tier) or t2.small
# OS: Ubuntu 22.04 LTS
# Security Group: Allow ports 80, 443, 8000
```

**SSH into instance and setup:**

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx
sudo apt install nginx -y

# Clone your repository
git clone https://github.com/yourusername/AutoWeb_Outreach_AI.git
cd AutoWeb_Outreach_AI/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# (paste your environment variables)

# Run database migrations
alembic upgrade head

# Install supervisor for process management
sudo apt install supervisor -y
```

**Create Supervisor Configuration:**

```bash
sudo nano /etc/supervisor/conf.d/autoweb.conf
```

```ini
[program:autoweb]
directory=/home/ubuntu/AutoWeb_Outreach_AI/backend
command=/home/ubuntu/AutoWeb_Outreach_AI/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/autoweb.err.log
stdout_logfile=/var/log/autoweb.out.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start autoweb
```

**Configure Nginx:**

```bash
sudo nano /etc/nginx/sites-available/autoweb
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/autoweb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 3: Deploy Frontend on S3 + CloudFront

```bash
# Build frontend
cd frontend
npm install
npm run build

# Install AWS CLI
pip install awscli

# Configure AWS CLI
aws configure

# Create S3 bucket
aws s3 mb s3://your-frontend-bucket

# Enable static website hosting
aws s3 website s3://your-frontend-bucket --index-document index.html

# Upload build files
aws s3 sync dist/ s3://your-frontend-bucket --acl public-read

# Create CloudFront distribution (optional, for CDN)
# Go to AWS CloudFront console and create distribution pointing to S3
```

**Done!** Your app is live on AWS.

---

## Option 4: DigitalOcean

### Step 1: Create Droplet

1. Go to DigitalOcean Console
2. Create Droplet:
   - Image: Ubuntu 22.04 LTS
   - Plan: Basic ($12/mo - 2GB RAM)
   - Add SSH key
   - Create Droplet

### Step 2: Create Managed PostgreSQL

1. Go to Databases
2. Create Database Cluster:
   - Engine: PostgreSQL 15
   - Plan: Basic ($15/mo)
   - Create Database

3. Note connection details

### Step 3: Deploy Backend

SSH into droplet:

```bash
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install python3.11 python3.11-venv python3-pip nginx supervisor git -y

# Clone repository
cd /var/www
git clone https://github.com/yourusername/AutoWeb_Outreach_AI.git
cd AutoWeb_Outreach_AI/backend

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with your environment variables
nano .env

# Run migrations
alembic upgrade head
```

**Follow same Nginx and Supervisor setup as AWS Option 3**

### Step 4: Deploy Frontend

```bash
# On your local machine
cd frontend
npm install
npm run build

# Upload to droplet
scp -r dist/* root@your-droplet-ip:/var/www/html/
```

**Configure Nginx for frontend:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/html;
    index index.html;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**Done!** Your app is live on DigitalOcean.

---

## Environment Variables

### Required Variables

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# API Keys (REQUIRED)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...

# Optional but recommended
UNSPLASH_API_KEY=...
PEXELS_API_KEY=...

# Security
SECRET_KEY=your-long-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
CORS_ORIGINS=["https://your-frontend.com","http://localhost:3000"]

# Environment
ENVIRONMENT=production
DEBUG=False
```

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Database Migration

### Initial Setup

```bash
# SSH into your server or use platform shell
cd backend

# Run migrations
alembic upgrade head

# Verify
alembic current
```

### Future Migrations

When you make database changes:

```bash
# Create migration
alembic revision --autogenerate -m "description of changes"

# Apply migration
alembic upgrade head
```

---

## Domain & SSL Setup

### Step 1: Point Domain to Server

Add DNS records:

```
Type  | Name | Value
------|------|-------
A     | @    | your-server-ip
A     | www  | your-server-ip
```

### Step 2: Install SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

Nginx will be automatically configured for HTTPS!

---

## Monitoring & Maintenance

### 1. Application Logs

```bash
# Supervisor logs
sudo tail -f /var/log/autoweb.out.log
sudo tail -f /var/log/autoweb.err.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Database Backups

**Automated Backups (PostgreSQL):**

```bash
# Create backup script
nano /root/backup-db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > /root/backups/backup_$DATE.sql
# Keep only last 7 days
find /root/backups -name "backup_*.sql" -mtime +7 -delete
```

```bash
chmod +x /root/backup-db.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add line:
0 2 * * * /root/backup-db.sh
```

### 3. Monitoring Tools

**Install monitoring (optional):**

```bash
# Uptime monitoring
# Sign up for https://uptimerobot.com (free)

# Application monitoring
pip install sentry-sdk
```

Add to `backend/app/main.py`:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### 4. Update Application

```bash
cd /var/www/AutoWeb_Outreach_AI
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo supervisorctl restart autoweb
```

---

## Troubleshooting

### Issue: Database Connection Failed

```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL

# Check firewall
sudo ufw status
```

### Issue: Application Won't Start

```bash
# Check logs
sudo supervisorctl tail autoweb stderr

# Check Python version
python3.11 --version

# Restart service
sudo supervisorctl restart autoweb
```

### Issue: CORS Errors

Update `CORS_ORIGINS` in `.env`:

```env
CORS_ORIGINS=["https://your-frontend.com","https://www.your-frontend.com"]
```

Restart application.

---

## Cost Estimates

### Railway
- **Hobby:** $5/mo (500 hours)
- **Pro:** $20/mo (unlimited)
- **Database:** Included

### Render
- **Free:** $0 (with limitations)
- **Starter:** $7/mo per service
- **Database:** $7/mo

### AWS
- **EC2 t2.micro:** $8-10/mo
- **RDS db.t3.micro:** $15-20/mo
- **Total:** $25-30/mo

### DigitalOcean
- **Droplet (2GB):** $12/mo
- **Managed PostgreSQL:** $15/mo
- **Total:** $27/mo

---

## Next Steps

1. **Choose your deployment platform**
2. **Set up environment variables**
3. **Deploy database first**
4. **Deploy backend**
5. **Deploy frontend**
6. **Configure domain & SSL**
7. **Set up monitoring**
8. **Create backup strategy**

---

## Support

If you encounter issues:
1. Check application logs
2. Verify environment variables
3. Test database connection
4. Check firewall rules
5. Review platform documentation

---

**Good luck with your deployment! 🚀**
