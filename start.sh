#!/bin/bash
# =============================================================================
# NEON CASINO - PRODUCTION DEPLOYMENT SCRIPT
# =============================================================================

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="neon-casino"
APP_DIR="/opt/neon-casino"
LOG_DIR="/var/log/neon-casino"
PID_FILE="/var/run/neon-casino.pid"
USER="neon-casino"
GROUP="neon-casino"
VENV_DIR="$APP_DIR/venv"
PYTHON_VERSION="3.11"
BACKUP_DIR="/opt/neon-casino-backups"
NGINX_CONF="/etc/nginx/sites-available/neon-casino"
SYSTEMD_SERVICE="/etc/systemd/system/neon-casino.service"

# Banner
echo -e "${PURPLE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    🎰 NEON CASINO 🎰                         ║"
echo "║              Enterprise Production Deployment                  ║"
echo "║                   v2.0.0 - Epic Edition                      ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# System updates and prerequisites
install_system_dependencies() {
    print_header "Installing system dependencies..."
    
    # Update system
    apt-get update -y
    apt-get upgrade -y
    
    # Install essential packages
    apt-get install -y \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        python3-pip \
        build-essential \
        libssl-dev \
        libffi-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libffi-dev \
        liblzma-dev \
        nginx \
        redis-server \
        postgresql \
        postgresql-contrib \
        ufw \
        fail2ban \
        htop \
        iotop \
        curl \
        wget \
        git \
        vim \
        tmux \
        supervisor \
        logrotate \
        rsync \
        zip \
        unzip \
        certbot \
        python3-certbot-nginx
    
    print_success "System dependencies installed"
}

# Create dedicated user and directories
setup_user_and_directories() {
    print_header "Setting up user and directories..."
    
    # Create user and group
    if ! id "$USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$APP_DIR" "$USER"
        print_status "Created user: $USER"
    fi
    
    # Create directories
    mkdir -p "$APP_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "/etc/neon-casino"
    
    # Set permissions
    chown -R "$USER:$GROUP" "$APP_DIR"
    chown -R "$USER:$GROUP" "$LOG_DIR"
    chown -R "$USER:$GROUP" "$BACKUP_DIR"
    
    print_success "User and directories configured"
}

# Install Python dependencies
install_python_dependencies() {
    print_header "Installing Python dependencies..."
    
    # Copy application files
    cp -r . "$APP_DIR/"
    chown -R "$USER:$GROUP" "$APP_DIR"
    
    # Create virtual environment
    sudo -u "$USER" python3.11 -m venv "$VENV_DIR"
    
    # Upgrade pip
    sudo -u "$USER" "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel
    
    # Install dependencies
    sudo -u "$USER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
    
    print_success "Python dependencies installed"
}

# Configure Firebase
configure_firebase() {
    print_header "Configuring Firebase..."
    
    # Secure Firebase credentials
    if [ -f "$APP_DIR/neonrollfirebase-service-account.json" ]; then
        chmod 600 "$APP_DIR/neonrollfirebase-service-account.json"
        chown "$USER:$GROUP" "$APP_DIR/neonrollfirebase-service-account.json"
        print_success "Firebase credentials secured"
    else
        print_warning "Firebase service account file not found"
    fi
}

# Configure Redis
configure_redis() {
    print_header "Configuring Redis..."
    
    # Redis configuration
    cat > /etc/redis/redis.conf.d/neon-casino.conf << EOF
# Neon Casino Redis Configuration
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename neon-casino.rdb
dir /var/lib/redis
requirepass neon-casino-redis-$(openssl rand -hex 32)
EOF
    
    # Restart Redis
    systemctl restart redis-server
    systemctl enable redis-server
    
    print_success "Redis configured"
}

# Configure PostgreSQL
configure_postgresql() {
    print_header "Configuring PostgreSQL..."
    
    # Create database and user
    sudo -u postgres psql << EOF
CREATE DATABASE neon_casino;
CREATE USER neon_casino WITH ENCRYPTED PASSWORD 'neon_casino_$(openssl rand -hex 16)';
GRANT ALL PRIVILEGES ON DATABASE neon_casino TO neon_casino;
\q
EOF
    
    print_success "PostgreSQL configured"
}

# Configure Nginx
configure_nginx() {
    print_header "Configuring Nginx..."
    
    # Create Nginx configuration
    cat > "$NGINX_CONF" << 'EOF'
server {
    listen 80;
    server_name agrobmin.com.ua www.agrobmin.com.ua;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' telegram.org; style-src 'self' 'unsafe-inline'; font-src 'self' data:; img-src 'self' data: https:; connect-src 'self' wss: https:;" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Root directory
    root /opt/neon-casino;
    index index.html;
    
    # Main location
    location / {
        try_files $uri $uri/ =404;
        
        # Cache static files
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API proxy (if needed)
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Webhook endpoint
    location /webhook/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Security
    location ~ /\. {
        deny all;
    }
    
    location ~* \.(py|sh|log|conf)$ {
        deny all;
    }
}
EOF
    
    # Enable site
    ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    nginx -t && systemctl reload nginx
    systemctl enable nginx
    
    print_success "Nginx configured"
}

# Configure SSL with Let's Encrypt
configure_ssl() {
    print_header "Configuring SSL certificate..."
    
    # Get SSL certificate
    certbot --nginx -d agrobmin.com.ua -d www.agrobmin.com.ua --non-interactive --agree-tos --email admin@agrobmin.com.ua
    
    # Setup automatic renewal
    cat > /etc/cron.d/certbot << EOF
0 12 * * * root certbot renew --quiet --deploy-hook "systemctl reload nginx"
EOF
    
    print_success "SSL certificate configured"
}

# Create systemd service
create_systemd_service() {
    print_header "Creating systemd service..."
    
    cat > "$SYSTEMD_SERVICE" << EOF
[Unit]
Description=Neon Casino Bot
After=network.target redis.service postgresql.service
Wants=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$APP_DIR
Environment=PATH=$VENV_DIR/bin
Environment=PYTHONPATH=$APP_DIR
ExecStart=$VENV_DIR/bin/python bot.py
ExecReload=/bin/kill -HUP \$MAINPID
ExecStop=/bin/kill -TERM \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=neon-casino

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR $LOG_DIR
CapabilityBoundingSet=
AmbientCapabilities=
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM
LockPersonality=true
MemoryDenyWriteExecute=true
RestrictRealtime=true
RestrictNamespaces=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
PrivateDevices=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable and start service
    systemctl daemon-reload
    systemctl enable "$APP_NAME"
    
    print_success "Systemd service created"
}

# Configure firewall
configure_firewall() {
    print_header "Configuring firewall..."
    
    # UFW configuration
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH
    ufw allow ssh
    
    # Allow HTTP/HTTPS
    ufw allow 'Nginx Full'
    
    # Allow specific ports if needed
    ufw allow 8080/tcp  # Bot webhook
    
    # Enable UFW
    ufw --force enable
    
    print_success "Firewall configured"
}

# Configure monitoring
configure_monitoring() {
    print_header "Configuring monitoring..."
    
    # Log rotation
    cat > /etc/logrotate.d/neon-casino << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $GROUP
    postrotate
        systemctl reload $APP_NAME
    endscript
}
EOF
    
    # Create monitoring script
    cat > /usr/local/bin/neon-casino-monitor << 'EOF'
#!/bin/bash
# Neon Casino Monitoring Script

LOG_FILE="/var/log/neon-casino/monitor.log"
SERVICE_NAME="neon-casino"

# Check if service is running
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "$(date): Service $SERVICE_NAME is not running. Attempting to restart..." >> $LOG_FILE
    systemctl restart $SERVICE_NAME
    sleep 10
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "$(date): Service $SERVICE_NAME restarted successfully" >> $LOG_FILE
    else
        echo "$(date): Failed to restart service $SERVICE_NAME" >> $LOG_FILE
    fi
fi

# Check memory usage
MEMORY_USAGE=$(ps -o pid,ppid,cmd,%mem,%cpu --sort=-%mem -C python3.11 | grep bot.py | awk '{print $4}')
if [ ! -z "$MEMORY_USAGE" ] && (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "$(date): High memory usage detected: $MEMORY_USAGE%" >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df /opt/neon-casino | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "$(date): High disk usage detected: $DISK_USAGE%" >> $LOG_FILE
fi
EOF
    
    chmod +x /usr/local/bin/neon-casino-monitor
    
    # Add to crontab
    cat > /etc/cron.d/neon-casino-monitor << EOF
*/5 * * * * root /usr/local/bin/neon-casino-monitor
EOF
    
    print_success "Monitoring configured"
}

# Backup configuration
configure_backup() {
    print_header "Configuring backup system..."
    
    # Create backup script
    cat > /usr/local/bin/neon-casino-backup << 'EOF'
#!/bin/bash
# Neon Casino Backup Script

BACKUP_DIR="/opt/neon-casino-backups"
APP_DIR="/opt/neon-casino"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/neon-casino-$DATE.tar.gz"

# Create backup
tar -czf "$BACKUP_FILE" \
    --exclude="$APP_DIR/venv" \
    --exclude="$APP_DIR/__pycache__" \
    --exclude="$APP_DIR/*.pyc" \
    --exclude="$APP_DIR/neon_casino.log" \
    "$APP_DIR"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "neon-casino-*.tar.gz" -mtime +7 -delete

# Log backup
echo "$(date): Backup created: $BACKUP_FILE" >> /var/log/neon-casino/backup.log
EOF
    
    chmod +x /usr/local/bin/neon-casino-backup
    
    # Add to crontab (daily backup at 2 AM)
    cat > /etc/cron.d/neon-casino-backup << EOF
0 2 * * * root /usr/local/bin/neon-casino-backup
EOF
    
    print_success "Backup system configured"
}

# Security hardening
configure_security() {
    print_header "Applying security hardening..."
    
    # Fail2ban configuration
    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF
    
    # Restart fail2ban
    systemctl restart fail2ban
    systemctl enable fail2ban
    
    # Secure shared memory
    echo "tmpfs /run/shm tmpfs defaults,noexec,nosuid 0 0" >> /etc/fstab
    
    print_success "Security hardening applied"
}

# Performance optimization
optimize_performance() {
    print_header "Optimizing performance..."
    
    # Kernel parameters
    cat > /etc/sysctl.d/99-neon-casino.conf << EOF
# Network optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.ipv4.tcp_window_scaling = 1
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# File system optimizations
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.swappiness = 10
fs.file-max = 65535
EOF
    
    sysctl -p /etc/sysctl.d/99-neon-casino.conf
    
    print_success "Performance optimized"
}

# Start the application
start_application() {
    print_header "Starting Neon Casino..."
    
    # Start and enable services
    systemctl start "$APP_NAME"
    systemctl enable "$APP_NAME"
    
    # Wait for startup
    sleep 5
    
    # Check status
    if systemctl is-active --quiet "$APP_NAME"; then
        print_success "Neon Casino started successfully!"
        
        # Display status
        echo -e "\n${GREEN}🎰 NEON CASINO DEPLOYMENT COMPLETE! 🎰${NC}"
        echo -e "${WHITE}════════════════════════════════════════════════════════════════${NC}"
        echo -e "${CYAN}📱 Bot URL:${NC} https://t.me/neonroll_casino_bot"
        echo -e "${CYAN}🌐 Web App:${NC} https://agrobmin.com.ua"
        echo -e "${CYAN}📊 Status:${NC} systemctl status $APP_NAME"
        echo -e "${CYAN}📋 Logs:${NC} journalctl -u $APP_NAME -f"
        echo -e "${CYAN}🔍 Monitor:${NC} tail -f $LOG_DIR/neon_casino.log"
        echo -e "${WHITE}════════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}✅ All systems operational!${NC}"
        echo -e "${YELLOW}🚀 Ready to accept players!${NC}"
        
    else
        print_error "Failed to start Neon Casino"
        echo "Check logs: journalctl -u $APP_NAME -n 50"
        exit 1
    fi
}

# Main execution
main() {
    print_header "Starting Neon Casino deployment..."
    
    check_root
    install_system_dependencies
    setup_user_and_directories
    install_python_dependencies
    configure_firebase
    configure_redis
    configure_postgresql
    configure_nginx
    configure_ssl
    create_systemd_service
    configure_firewall
    configure_monitoring
    configure_backup
    configure_security
    optimize_performance
    start_application
    
    print_success "Deployment completed successfully!"
}

# Execute main function
main "$@"
