#!/bin/bash

# ============================================================================
# AutoWeb Outreach AI - Automated Deployment Script for Ubuntu VPS
# ============================================================================
# This script automates the deployment of AutoWeb Outreach AI on Ubuntu 22.04
# Run this script as root or with sudo privileges
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
PROJECT_DIR="/var/www/AutoWeb_Outreach_AI"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_DIR="/var/log/autoweb"
DB_NAME="autoweb_production"
DB_USER="autoweb_user"

# Functions
print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root or with sudo"
    exit 1
fi

print_header "AutoWeb Outreach AI - Deployment Script"

# ============================================================================
# STEP 1: System Update
# ============================================================================
print_header "Step 1: Updating System Packages"
apt update && apt upgrade -y
print_success "System updated successfully"

# ============================================================================
# STEP 2: Install Required Software
# ============================================================================
print_header "Step 2: Installing Required Software"

# Install Python 3.11
print_warning "Installing Python 3.11..."
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
print_success "Python 3.11 installed"

# Install Node.js 20.x
print_warning "Installing Node.js 20.x..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
print_success "Node.js $(node --version) installed"

# Install PostgreSQL 15
print_warning "Installing PostgreSQL 15..."
apt install -y postgresql postgresql-contrib
print_success "PostgreSQL installed"

# Install Redis
print_warning "Installing Redis..."
apt install -y redis-server
print_success "Redis installed"

# Install Nginx
print_warning "Installing Nginx..."
apt install -y nginx
print_success "Nginx installed"

# Install Git
apt install -y git curl wget
print_success "Additional tools installed"

# ============================================================================
# STEP 3: Configure PostgreSQL
# ============================================================================
print_header "Step 3: Configuring PostgreSQL Database"

# Generate random password for database
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Create database and user
sudo -u postgres psql << EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
\q
EOF

print_success "PostgreSQL database configured"
print_warning "Database credentials:"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo "  Save these credentials! You'll need them for .env file"

# ============================================================================
# STEP 4: Configure Redis
# ============================================================================
print_header "Step 4: Configuring Redis"
systemctl enable redis-server
systemctl start redis-server
print_success "Redis configured and started"

# ============================================================================
# STEP 5: Create Project Directory
# ============================================================================
print_header "Step 5: Setting Up Project Directory"

# Create project directory
mkdir -p $PROJECT_DIR
mkdir -p $LOG_DIR

print_success "Project directories created"

# ============================================================================
# STEP 6: Deploy Application Code
# ============================================================================
print_header "Step 6: Deploying Application Code"

print_warning "Please upload your code to $PROJECT_DIR using one of these methods:"
echo ""
echo "Option 1: Using Git (Recommended)"
echo "  git clone https://github.com/yourusername/AutoWeb_Outreach_AI.git $PROJECT_DIR"
echo ""
echo "Option 2: Using SCP from your local machine"
echo "  scp -r /path/to/AutoWeb_Outreach_AI root@YOUR_SERVER_IP:$PROJECT_DIR"
echo ""
echo "Option 3: Using SFTP client (FileZilla, WinSCP, etc.)"
echo "  Upload to: $PROJECT_DIR"
echo ""

read -p "Press Enter once you've uploaded the code..."

# Verify code exists
if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Backend or Frontend directory not found!"
    print_error "Please ensure code is uploaded to $PROJECT_DIR"
    exit 1
fi

print_success "Code verified"

# ============================================================================
# STEP 7: Setup Backend
# ============================================================================
print_header "Step 7: Setting Up Backend"

cd $BACKEND_DIR

# Create virtual environment
print_warning "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_warning "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

# Generate SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Create .env file
print_warning "Creating backend .env file..."
cat > .env << EOF
APP_NAME="AutoWeb Outreach AI API"
API_VERSION=0.1.0
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

OPENAI_API_KEY=REPLACE_WITH_YOUR_OPENAI_KEY
EOF

chmod 600 .env
print_success "Backend .env file created"

print_warning "IMPORTANT: Edit $BACKEND_DIR/.env and add your API keys!"
print_warning "Required: OPENAI_API_KEY"
print_warning "Optional: GOOGLE_API_KEY, UNSPLASH_API_KEY, PEXELS_API_KEY"

# Run database migrations
print_warning "Running database migrations..."
source venv/bin/activate
alembic upgrade head
print_success "Database migrations completed"

# ============================================================================
# STEP 8: Setup Frontend
# ============================================================================
print_header "Step 8: Setting Up Frontend"

cd $FRONTEND_DIR

# Create .env file
print_warning "Creating frontend .env file..."
cat > .env << EOF
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
EOF

print_warning "Installing Node.js dependencies..."
npm install
print_success "Node.js dependencies installed"

print_warning "Building Next.js application..."
npm run build
print_success "Frontend built successfully"

# ============================================================================
# STEP 9: Configure Systemd Services
# ============================================================================
print_header "Step 9: Configuring Systemd Services"

# Copy service files
if [ -f "$PROJECT_DIR/deployment/autoweb-backend.service" ]; then
    cp $PROJECT_DIR/deployment/autoweb-backend.service /etc/systemd/system/
    print_success "Backend service file copied"
else
    print_error "Backend service file not found!"
fi

if [ -f "$PROJECT_DIR/deployment/autoweb-frontend.service" ]; then
    cp $PROJECT_DIR/deployment/autoweb-frontend.service /etc/systemd/system/
    print_success "Frontend service file copied"
else
    print_error "Frontend service file not found!"
fi

# Set permissions
chown -R www-data:www-data $PROJECT_DIR
chown -R www-data:www-data $LOG_DIR

# Reload systemd
systemctl daemon-reload

# Enable and start services
systemctl enable autoweb-backend
systemctl enable autoweb-frontend

systemctl start autoweb-backend
systemctl start autoweb-frontend

print_success "Services configured and started"

# ============================================================================
# STEP 10: Configure Nginx
# ============================================================================
print_header "Step 10: Configuring Nginx"

# Copy nginx config
if [ -f "$PROJECT_DIR/deployment/nginx.conf" ]; then
    cp $PROJECT_DIR/deployment/nginx.conf /etc/nginx/sites-available/autoweb

    # Create symlink
    ln -sf /etc/nginx/sites-available/autoweb /etc/nginx/sites-enabled/autoweb

    # Remove default site
    rm -f /etc/nginx/sites-enabled/default

    print_success "Nginx configuration copied"
else
    print_error "Nginx config file not found!"
fi

# Test nginx configuration
nginx -t
if [ $? -eq 0 ]; then
    print_success "Nginx configuration is valid"
    systemctl restart nginx
    print_success "Nginx restarted"
else
    print_error "Nginx configuration has errors!"
    exit 1
fi

# ============================================================================
# STEP 11: Configure Firewall
# ============================================================================
print_header "Step 11: Configuring Firewall"

ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

print_success "Firewall configured"

# ============================================================================
# STEP 12: SSL Certificate (Let's Encrypt)
# ============================================================================
print_header "Step 12: SSL Certificate Setup"

print_warning "To enable HTTPS with Let's Encrypt:"
echo ""
echo "1. Point your domain to this server's IP address"
echo "2. Wait for DNS propagation (can take up to 48 hours)"
echo "3. Run these commands:"
echo ""
echo "   sudo apt install certbot python3-certbot-nginx -y"
echo "   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com"
echo ""
echo "4. Certbot will automatically configure SSL and renew certificates"
echo ""

# ============================================================================
# DEPLOYMENT COMPLETE
# ============================================================================
print_header "🎉 Deployment Complete!"

echo ""
print_success "Application deployed successfully!"
echo ""
echo "Next Steps:"
echo ""
echo "1. Edit backend .env file:"
echo "   sudo nano $BACKEND_DIR/.env"
echo "   - Add your OPENAI_API_KEY"
echo "   - Update CORS_ORIGINS with your domain"
echo ""
echo "2. Edit frontend .env file:"
echo "   sudo nano $FRONTEND_DIR/.env"
echo "   - Update NEXT_PUBLIC_API_URL with your domain"
echo ""
echo "3. Edit Nginx config:"
echo "   sudo nano /etc/nginx/sites-available/autoweb"
echo "   - Replace 'yourdomain.com' with your actual domain"
echo ""
echo "4. Restart services:"
echo "   sudo systemctl restart autoweb-backend"
echo "   sudo systemctl restart autoweb-frontend"
echo "   sudo systemctl restart nginx"
echo ""
echo "5. Set up SSL certificate (after DNS is configured):"
echo "   sudo apt install certbot python3-certbot-nginx -y"
echo "   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com"
echo ""
echo "6. Check service status:"
echo "   sudo systemctl status autoweb-backend"
echo "   sudo systemctl status autoweb-frontend"
echo ""
echo "7. View logs:"
echo "   sudo journalctl -u autoweb-backend -f"
echo "   sudo journalctl -u autoweb-frontend -f"
echo ""
echo "Database Credentials (SAVE THESE!):"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo "  Connection: postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
print_success "Your application will be available at: https://yourdomain.com"
echo ""
