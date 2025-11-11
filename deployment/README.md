# AutoWeb Outreach AI - Deployment Files

This directory contains all the files needed to deploy AutoWeb Outreach AI to an Ubuntu VPS server.

## Files in This Directory

### 1. **UBUNTU_VPS_DEPLOYMENT_GUIDE.md** ⭐ START HERE
Complete step-by-step guide for deploying to Ubuntu 22.04 VPS.
- Quick automated deployment
- Manual step-by-step deployment
- Post-deployment configuration
- SSL setup
- Troubleshooting

### 2. **deploy.sh**
Automated deployment script that handles:
- System updates
- Software installation (Python, Node.js, PostgreSQL, Redis, Nginx)
- Database configuration
- Service setup
- Firewall configuration

**Usage:**
```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

### 3. **production.env.backend**
Production environment variables template for backend.
- Copy to `/var/www/AutoWeb_Outreach_AI/backend/.env`
- Update with your actual values (API keys, domain, etc.)

### 4. **production.env.frontend**
Production environment variables template for frontend.
- Copy to `/var/www/AutoWeb_Outreach_AI/frontend/.env`
- Update with your actual domain

### 5. **autoweb-backend.service**
Systemd service file for backend (FastAPI).
- Copy to `/etc/systemd/system/autoweb-backend.service`
- Manages backend application lifecycle

### 6. **autoweb-frontend.service**
Systemd service file for frontend (Next.js).
- Copy to `/etc/systemd/system/autoweb-frontend.service`
- Manages frontend application lifecycle

### 7. **nginx.conf**
Nginx reverse proxy configuration.
- Copy to `/etc/nginx/sites-available/autoweb`
- Handles HTTP/HTTPS requests
- Routes traffic to backend and frontend

## Quick Start

### Option 1: Automated Deployment (Recommended)

1. SSH into your Ubuntu VPS:
   ```bash
   ssh root@YOUR_SERVER_IP
   ```

2. Upload your project to the server

3. Run the deployment script:
   ```bash
   cd /var/www/AutoWeb_Outreach_AI/deployment
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

4. Follow the post-deployment steps in the guide

### Option 2: Manual Deployment

Follow the complete step-by-step guide in `UBUNTU_VPS_DEPLOYMENT_GUIDE.md`

## Prerequisites

- Ubuntu 22.04 LTS VPS
- Minimum 2GB RAM
- Domain name pointing to server IP
- OpenAI API key
- Root or sudo access

## What Gets Deployed

- **Backend**: FastAPI application running on port 8000
- **Frontend**: Next.js application running on port 3000
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Web Server**: Nginx (reverse proxy)
- **SSL**: Let's Encrypt (optional, configured separately)

## Architecture

```
Internet
    ↓
Nginx (443/80)
    ↓
    ├→ Frontend (Next.js:3000) → /
    └→ Backend (FastAPI:8000)  → /api
           ↓
    PostgreSQL (5432)
    Redis (6379)
```

## Post-Deployment Tasks

1. **Configure API Keys**
   - Edit `/var/www/AutoWeb_Outreach_AI/backend/.env`
   - Add your OpenAI API key

2. **Update Domain**
   - Update Nginx config with your domain
   - Update backend CORS_ORIGINS
   - Update frontend API URL

3. **Set Up SSL**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

4. **Create First User**
   - Via API or frontend registration page

## Useful Commands

```bash
# Check service status
sudo systemctl status autoweb-backend
sudo systemctl status autoweb-frontend

# Restart services
sudo systemctl restart autoweb-backend
sudo systemctl restart autoweb-frontend
sudo systemctl restart nginx

# View logs
sudo journalctl -u autoweb-backend -f
sudo journalctl -u autoweb-frontend -f
sudo tail -f /var/log/nginx/autoweb-error.log

# Test Nginx config
sudo nginx -t

# Backup database
sudo -u postgres pg_dump autoweb_production > backup.sql
```

## Troubleshooting

See the **Troubleshooting** section in `UBUNTU_VPS_DEPLOYMENT_GUIDE.md` for:
- Service won't start
- Database connection issues
- Nginx errors
- CORS problems
- SSL certificate issues

## Security Notes

- All `.env` files should have `chmod 600` permissions
- Database passwords are auto-generated during deployment
- Firewall is configured to allow only ports 22, 80, 443
- Services run as `www-data` user (not root)

## Support

For issues or questions:
1. Check the deployment guide
2. Review application logs
3. Verify all services are running
4. Check database connectivity

## Directory Structure After Deployment

```
/var/www/AutoWeb_Outreach_AI/
├── backend/
│   ├── app/
│   ├── venv/
│   ├── .env (you create this)
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── node_modules/
│   ├── .env (you create this)
│   └── package.json
└── deployment/ (this directory)

/etc/systemd/system/
├── autoweb-backend.service
└── autoweb-frontend.service

/etc/nginx/sites-available/
└── autoweb

/var/log/autoweb/
├── backend.log
├── backend-error.log
├── frontend.log
└── frontend-error.log
```

---

**Ready to deploy? Start with `UBUNTU_VPS_DEPLOYMENT_GUIDE.md`!**
