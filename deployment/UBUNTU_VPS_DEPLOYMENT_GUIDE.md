# AutoWeb Outreach AI - Ubuntu VPS Deployment Guide

Complete step-by-step guide to deploy AutoWeb Outreach AI on Ubuntu 22.04 VPS server.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Deployment (Automated)](#quick-deployment-automated)
3. [Manual Deployment (Step-by-Step)](#manual-deployment-step-by-step)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [SSL Certificate Setup](#ssl-certificate-setup)
6. [Maintenance & Monitoring](#maintenance--monitoring)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Server Requirements

- **Operating System**: Ubuntu 22.04 LTS (64-bit)
- **RAM**: Minimum 2GB (4GB recommended)
- **CPU**: Minimum 1 vCPU (2 vCPUs recommended)
- **Storage**: Minimum 20GB SSD
- **Network**: Static IP address

### 2. Domain Setup

- Domain name pointing to your VPS IP address
- DNS A records configured:
  - `@` (root domain) → Your VPS IP
  - `www` → Your VPS IP

### 3. Required Credentials

- OpenAI API key (REQUIRED)
- Optional: Google API key, Unsplash API key, Pexels API key

### 4. Local Requirements

- Git installed on your local machine
- SSH client (PuTTY for Windows, Terminal for Mac/Linux)
- SFTP client (FileZilla, WinSCP) - optional

---

## Quick Deployment (Automated)

The fastest way to deploy using the automated script.

### Step 1: SSH into Your Server

```bash
ssh root@YOUR_SERVER_IP
```

### Step 2: Upload Deployment Files

**Option A: Using Git (Recommended)**

```bash
cd /tmp
git clone https://github.com/yourusername/AutoWeb_Outreach_AI.git
cd AutoWeb_Outreach_AI/deployment
chmod +x deploy.sh
```

**Option B: Using SCP from Local Machine**

```bash
# From your local machine
scp -r "C:\Users\rabia\Documents\project AutoWeb Outreach AI\AutoWeb_Outreach_AI" root@YOUR_SERVER_IP:/tmp/
```

### Step 3: Run Deployment Script

```bash
sudo bash deploy.sh
```

The script will:
- Install all required software (Python, Node.js, PostgreSQL, Redis, Nginx)
- Configure database and create credentials
- Set up project directories
- Install dependencies
- Configure systemd services
- Set up Nginx reverse proxy
- Configure firewall

### Step 4: Complete Configuration

After the script finishes, you need to:

1. **Edit Backend Environment Variables**

```bash
sudo nano /var/www/AutoWeb_Outreach_AI/backend/.env
```

Update:
- `OPENAI_API_KEY=your-actual-key`
- `CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`

2. **Edit Frontend Environment Variables**

```bash
sudo nano /var/www/AutoWeb_Outreach_AI/frontend/.env
```

Update:
- `NEXT_PUBLIC_API_URL=https://yourdomain.com/api`

3. **Edit Nginx Configuration**

```bash
sudo nano /etc/nginx/sites-available/autoweb
```

Replace all instances of `yourdomain.com` with your actual domain.

4. **Restart Services**

```bash
sudo systemctl restart autoweb-backend
sudo systemctl restart autoweb-frontend
sudo systemctl restart nginx
```

5. **Set Up SSL** (See [SSL Certificate Setup](#ssl-certificate-setup))

---

## Manual Deployment (Step-by-Step)

Follow these steps if you prefer manual deployment or if the automated script fails.

### Step 1: Connect to Your VPS

```bash
ssh root@YOUR_SERVER_IP
```

### Step 2: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3: Install Python 3.11

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
python3.11 --version
```

### Step 4: Install Node.js 20.x

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install -y nodejs
node --version
npm --version
```

### Step 5: Install PostgreSQL 15

```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

**Configure PostgreSQL Database:**

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell, run:
CREATE USER autoweb_user WITH PASSWORD 'your_secure_password_here';
CREATE DATABASE autoweb_production OWNER autoweb_user;
GRANT ALL PRIVILEGES ON DATABASE autoweb_production TO autoweb_user;
ALTER USER autoweb_user CREATEDB;
\q
```

**Save your database credentials!**

### Step 6: Install Redis

```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### Step 7: Install Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Step 8: Install Additional Tools

```bash
sudo apt install -y git curl wget
```

### Step 9: Create Project Directory

```bash
sudo mkdir -p /var/www/AutoWeb_Outreach_AI
sudo mkdir -p /var/log/autoweb
```

### Step 10: Upload Your Code

**Option A: Using Git**

```bash
cd /var/www
sudo git clone https://github.com/yourusername/AutoWeb_Outreach_AI.git
```

**Option B: Using SCP from Local Machine**

```bash
# From your local machine (Windows PowerShell or Command Prompt)
scp -r "C:\Users\rabia\Documents\project AutoWeb Outreach AI\AutoWeb_Outreach_AI" root@YOUR_SERVER_IP:/var/www/
```

**Option C: Using SFTP Client (FileZilla, WinSCP)**

1. Open FileZilla/WinSCP
2. Connect to your server (IP, username: root, password)
3. Navigate to `/var/www/`
4. Upload the `AutoWeb_Outreach_AI` folder

### Step 11: Set Up Backend

```bash
cd /var/www/AutoWeb_Outreach_AI/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Create Backend .env File:**

```bash
nano .env
```

Paste the following (replace with your actual values):

```env
APP_NAME="AutoWeb Outreach AI API"
API_VERSION=0.1.0
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Replace with your actual database credentials from Step 5
DATABASE_URL=postgresql://autoweb_user:your_secure_password_here@localhost:5432/autoweb_production

# Generate a secure key: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7

# Replace with your actual domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# REQUIRED: Your OpenAI API key
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

Save with `Ctrl+O`, then `Enter`, then exit with `Ctrl+X`.

**Set correct permissions:**

```bash
chmod 600 .env
```

**Generate a SECRET_KEY:**

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and update your `.env` file.

**Run Database Migrations:**

```bash
source venv/bin/activate
alembic upgrade head
```

### Step 12: Set Up Frontend

```bash
cd /var/www/AutoWeb_Outreach_AI/frontend

# Install dependencies
npm install

# Create .env file
nano .env
```

Paste the following:

```env
# Replace with your actual domain
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
```

Save and exit.

**Build the frontend:**

```bash
npm run build
```

### Step 13: Configure Systemd Services

**Backend Service:**

```bash
sudo cp /var/www/AutoWeb_Outreach_AI/deployment/autoweb-backend.service /etc/systemd/system/
```

**Frontend Service:**

```bash
sudo cp /var/www/AutoWeb_Outreach_AI/deployment/autoweb-frontend.service /etc/systemd/system/
```

**Set Permissions:**

```bash
sudo chown -R www-data:www-data /var/www/AutoWeb_Outreach_AI
sudo chown -R www-data:www-data /var/log/autoweb
```

**Enable and Start Services:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable autoweb-backend
sudo systemctl enable autoweb-frontend

# Start services
sudo systemctl start autoweb-backend
sudo systemctl start autoweb-frontend

# Check status
sudo systemctl status autoweb-backend
sudo systemctl status autoweb-frontend
```

### Step 14: Configure Nginx

**Copy Nginx configuration:**

```bash
sudo cp /var/www/AutoWeb_Outreach_AI/deployment/nginx.conf /etc/nginx/sites-available/autoweb
```

**Edit the configuration:**

```bash
sudo nano /etc/nginx/sites-available/autoweb
```

Replace **ALL** instances of `yourdomain.com` with your actual domain name.

**Enable the site:**

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/autoweb /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# If test is successful, restart Nginx
sudo systemctl restart nginx
```

### Step 15: Configure Firewall

```bash
# Allow SSH (IMPORTANT - do this first!)
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## Post-Deployment Configuration

### Create First User

You can create your first user via the API:

```bash
curl -X POST https://yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@yourdomain.com",
    "password": "SecurePassword123!"
  }'
```

Or use the frontend registration page at `https://yourdomain.com/register`

### Verify Deployment

1. **Check API Health:**

```bash
curl https://yourdomain.com/api/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production",
  "timestamp": "...",
  "database": "connected"
}
```

2. **Check Frontend:**

Visit `https://yourdomain.com` in your browser. You should see the login page.

3. **Check API Documentation (if DEBUG=True):**

Visit `https://yourdomain.com/docs`

---

## SSL Certificate Setup

### Using Let's Encrypt (Free SSL)

**Step 1: Install Certbot**

```bash
sudo apt install -y certbot python3-certbot-nginx
```

**Step 2: Obtain Certificate**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts:
- Enter your email address
- Agree to Terms of Service
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

**Step 3: Verify Auto-Renewal**

```bash
sudo certbot renew --dry-run
```

Certbot will automatically renew certificates before they expire.

**Certificate Locations:**
- Certificate: `/etc/letsencrypt/live/yourdomain.com/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/yourdomain.com/privkey.pem`

---

## Maintenance & Monitoring

### Check Service Status

```bash
# Backend status
sudo systemctl status autoweb-backend

# Frontend status
sudo systemctl status autoweb-frontend

# Nginx status
sudo systemctl status nginx

# PostgreSQL status
sudo systemctl status postgresql

# Redis status
sudo systemctl status redis-server
```

### View Logs

**Application Logs:**

```bash
# Backend logs
sudo tail -f /var/log/autoweb/backend.log
sudo tail -f /var/log/autoweb/backend-error.log

# Frontend logs
sudo tail -f /var/log/autoweb/frontend.log
sudo tail -f /var/log/autoweb/frontend-error.log

# Systemd journal logs
sudo journalctl -u autoweb-backend -f
sudo journalctl -u autoweb-frontend -f
```

**Nginx Logs:**

```bash
sudo tail -f /var/log/nginx/autoweb-access.log
sudo tail -f /var/log/nginx/autoweb-error.log
```

**PostgreSQL Logs:**

```bash
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Restart Services

```bash
# Restart backend
sudo systemctl restart autoweb-backend

# Restart frontend
sudo systemctl restart autoweb-frontend

# Restart Nginx
sudo systemctl restart nginx

# Restart all
sudo systemctl restart autoweb-backend autoweb-frontend nginx
```

### Database Backup

**Create Backup:**

```bash
# Create backup directory
mkdir -p ~/backups

# Backup database
sudo -u postgres pg_dump autoweb_production > ~/backups/autoweb_backup_$(date +%Y%m%d_%H%M%S).sql
```

**Restore from Backup:**

```bash
sudo -u postgres psql autoweb_production < ~/backups/autoweb_backup_YYYYMMDD_HHMMSS.sql
```

**Automated Daily Backups:**

Create a backup script:

```bash
sudo nano /usr/local/bin/backup-autoweb.sh
```

Paste:

```bash
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump autoweb_production > $BACKUP_DIR/autoweb_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "autoweb_backup_*.sql" -mtime +7 -delete
```

Make it executable:

```bash
sudo chmod +x /usr/local/bin/backup-autoweb.sh
```

Add to crontab (runs daily at 2 AM):

```bash
sudo crontab -e
```

Add line:

```
0 2 * * * /usr/local/bin/backup-autoweb.sh
```

### Update Application

**Pull Latest Changes:**

```bash
cd /var/www/AutoWeb_Outreach_AI
git pull origin main
```

**Update Backend:**

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart autoweb-backend
```

**Update Frontend:**

```bash
cd ../frontend
npm install
npm run build
sudo systemctl restart autoweb-frontend
```

### Monitor Resource Usage

```bash
# CPU and Memory usage
htop

# Disk usage
df -h

# Service resource usage
systemctl status autoweb-backend autoweb-frontend

# Database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('autoweb_production'));"
```

---

## Troubleshooting

### Backend Won't Start

**Check logs:**

```bash
sudo journalctl -u autoweb-backend -n 50
sudo tail -n 50 /var/log/autoweb/backend-error.log
```

**Common issues:**

1. **Database connection failed**
   - Verify DATABASE_URL in .env
   - Check PostgreSQL is running: `sudo systemctl status postgresql`
   - Test connection: `sudo -u postgres psql autoweb_production`

2. **Missing dependencies**
   ```bash
   cd /var/www/AutoWeb_Outreach_AI/backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Permission issues**
   ```bash
   sudo chown -R www-data:www-data /var/www/AutoWeb_Outreach_AI
   ```

4. **Port 8000 already in use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

### Frontend Won't Start

**Check logs:**

```bash
sudo journalctl -u autoweb-frontend -n 50
sudo tail -n 50 /var/log/autoweb/frontend-error.log
```

**Common issues:**

1. **Build failed**
   ```bash
   cd /var/www/AutoWeb_Outreach_AI/frontend
   npm install
   npm run build
   ```

2. **Port 3000 already in use**
   ```bash
   sudo lsof -i :3000
   sudo kill -9 <PID>
   ```

### Nginx Errors

**Check configuration:**

```bash
sudo nginx -t
```

**Check logs:**

```bash
sudo tail -n 50 /var/log/nginx/error.log
```

**Restart Nginx:**

```bash
sudo systemctl restart nginx
```

### Database Issues

**Can't connect to database:**

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check database exists
sudo -u postgres psql -l | grep autoweb
```

**Reset database password:**

```bash
sudo -u postgres psql
ALTER USER autoweb_user WITH PASSWORD 'new_password';
\q

# Update .env file with new password
sudo nano /var/www/AutoWeb_Outreach_AI/backend/.env
```

### CORS Errors

If you see CORS errors in browser console:

1. Check backend .env:
   ```bash
   sudo nano /var/www/AutoWeb_Outreach_AI/backend/.env
   ```

   Ensure `CORS_ORIGINS` includes your domain:
   ```
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

2. Restart backend:
   ```bash
   sudo systemctl restart autoweb-backend
   ```

### SSL Certificate Issues

**Certificate not working:**

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

### Out of Memory

**Check memory usage:**

```bash
free -h
```

**Add swap space (if needed):**

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Check All Services

Quick script to check everything:

```bash
cat > ~/check-autoweb.sh << 'EOF'
#!/bin/bash
echo "=== AutoWeb System Status ==="
echo ""
echo "Backend Service:"
systemctl is-active autoweb-backend
echo ""
echo "Frontend Service:"
systemctl is-active autoweb-frontend
echo ""
echo "Nginx:"
systemctl is-active nginx
echo ""
echo "PostgreSQL:"
systemctl is-active postgresql
echo ""
echo "Redis:"
systemctl is-active redis-server
echo ""
echo "API Health Check:"
curl -s https://yourdomain.com/api/health | python3 -m json.tool
EOF

chmod +x ~/check-autoweb.sh
~/check-autoweb.sh
```

---

## Support Checklist

Before asking for help, verify:

- [ ] All services are running
- [ ] No errors in logs
- [ ] Database connection works
- [ ] .env files have correct values
- [ ] Domain DNS is configured correctly
- [ ] SSL certificate is valid
- [ ] Firewall allows traffic on ports 80, 443
- [ ] Sufficient disk space and memory

---

## Quick Reference Commands

```bash
# Service management
sudo systemctl status autoweb-backend
sudo systemctl restart autoweb-backend
sudo systemctl stop autoweb-backend
sudo systemctl start autoweb-backend

# View logs
sudo journalctl -u autoweb-backend -f
sudo journalctl -u autoweb-frontend -f

# Nginx
sudo nginx -t
sudo systemctl reload nginx

# Database
sudo -u postgres psql autoweb_production

# Check ports
sudo lsof -i :8000  # Backend
sudo lsof -i :3000  # Frontend
sudo lsof -i :80    # HTTP
sudo lsof -i :443   # HTTPS
```

---

## Security Recommendations

1. **Change default SSH port** (optional)
2. **Disable root SSH login**
3. **Set up fail2ban** for SSH brute-force protection
4. **Regular security updates**: `sudo apt update && sudo apt upgrade`
5. **Monitor logs regularly**
6. **Use strong passwords** for database and users
7. **Backup regularly**
8. **Keep API keys secure** in .env files with chmod 600

---

**Your application should now be fully deployed and accessible at `https://yourdomain.com`!**

**Good luck with your deployment! 🚀**
