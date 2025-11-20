#!/bin/bash
# GSM Dialler Installation Script
# This script installs and configures the GSM Dialler system on a fresh Raspberry Pi

set -e  # Exit on error

echo "=========================================="
echo "GSM Dialler Installation Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_DIR="/home/pi/gsm-dialler"

echo -e "${GREEN}Step 1: Installing system dependencies...${NC}"
apt-get update
apt-get install -y \
    apache2 \
    php \
    libapache2-mod-php \
    python3 \
    python3-pip \
    python3-rpi.gpio \
    python3-serial \
    minicom \
    git

echo -e "${GREEN}Step 2: Installing Python packages...${NC}"
pip3 install pyserial RPi.GPIO gpiozero

echo -e "${GREEN}Step 3: Creating directory structure...${NC}"
mkdir -p /var/www/html
mkdir -p /var/www/gsmdialler-data
mkdir -p /usr/local/bin
mkdir -p /etc/systemd/system

echo -e "${GREEN}Step 4: Copying web interface files...${NC}"
cp -r "$SCRIPT_DIR/../*.php" /var/www/html/ 2>/dev/null || true
cp "$SCRIPT_DIR/../index.php" /var/www/html/
cp "$SCRIPT_DIR/../login.php" /var/www/html/
cp "$SCRIPT_DIR/../logout.php" /var/www/html/
cp "$SCRIPT_DIR/../auth.php" /var/www/html/

echo -e "${GREEN}Step 5: Copying Python scripts...${NC}"
cp "$SCRIPT_DIR/../test_call.py" /var/www/html/
cp "$SCRIPT_DIR/../test_sms.py" /var/www/html/
cp "$SCRIPT_DIR/../gpio_trigger.py" /var/www/html/
cp "$SCRIPT_DIR/../power_on_modem.py" /usr/local/bin/

# Make scripts executable
chmod +x /var/www/html/*.py
chmod +x /usr/local/bin/power_on_modem.py

# Set ownership
chown -R www-data:www-data /var/www/html
chown -R www-data:www-data /var/www/gsmdialler-data
chown pi:pi /var/www/html/*.py 2>/dev/null || true

echo -e "${GREEN}Step 6: Creating data files...${NC}"
if [ ! -f /var/www/gsmdialler-data/call_list.txt ]; then
    touch /var/www/gsmdialler-data/call_list.txt
    echo "# Add phone numbers here, one per line" > /var/www/gsmdialler-data/call_list.txt
fi

if [ ! -f /var/www/gsmdialler-data/message.txt ]; then
    echo "Fire alarm triggered. Please respond immediately." > /var/www/gsmdialler-data/message.txt
fi

if [ ! -f /var/www/gsmdialler-data/log.txt ]; then
    touch /var/www/gsmdialler-data/log.txt
fi

chown -R www-data:www-data /var/www/gsmdialler-data

echo -e "${GREEN}Step 7: Setting up systemd services...${NC}"

# Create modem-power.service
if [ -f "$SCRIPT_DIR/../modem-power.service" ]; then
    cp "$SCRIPT_DIR/../modem-power.service" /etc/systemd/system/
else
    cat > /etc/systemd/system/modem-power.service << 'EOF'
[Unit]
Description=Power on GSM modem via GPIO
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/power_on_modem.py
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
EOF
fi

# Create gpio-trigger.service
if [ -f "$SCRIPT_DIR/../gpio-trigger.service" ]; then
    cp "$SCRIPT_DIR/../gpio-trigger.service" /etc/systemd/system/
else
    cat > /etc/systemd/system/gpio-trigger.service << 'EOF'
[Unit]
Description=GPIO Trigger Monitor for Fire Alarm
After=multi-user.target modem-power.service
Requires=modem-power.service

[Service]
ExecStart=/usr/bin/python3 /var/www/html/gpio_trigger.py
Restart=always
RestartSec=10
User=pi
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
fi

echo -e "${GREEN}Step 8: Configuring Apache...${NC}"
# Enable PHP module
a2enmod php
a2enmod rewrite

# Configure Apache to allow Python CGI (if needed)
# For now, we'll use direct Python execution

# Restart Apache
systemctl restart apache2
systemctl enable apache2

echo -e "${GREEN}Step 9: Configuring serial port...${NC}"
# Disable serial console if enabled
systemctl stop serial-getty@ttyAMA0.service 2>/dev/null || true
systemctl disable serial-getty@ttyAMA0.service 2>/dev/null || true
systemctl stop serial-getty@serial0.service 2>/dev/null || true
systemctl disable serial-getty@serial0.service 2>/dev/null || true

# Add user to dialout group for serial access
usermod -a -G dialout www-data
usermod -a -G dialout pi

echo -e "${GREEN}Step 10: Enabling services...${NC}"
systemctl daemon-reload
systemctl enable modem-power.service
systemctl enable gpio-trigger.service
systemctl start modem-power.service
systemctl start gpio-trigger.service

echo ""
echo -e "${GREEN}=========================================="
echo "Installation Complete!"
echo "==========================================${NC}"
echo ""
echo "System Status:"
systemctl status modem-power.service --no-pager -l | head -5
echo ""
systemctl status gpio-trigger.service --no-pager -l | head -5
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Access web interface: http://$(hostname -I | awk '{print $1}')/login.php"
echo "   Username: admin"
echo "   Password: dialler123"
echo ""
echo "2. Configure call list and message via web interface"
echo ""
echo "3. Test GPIO trigger by connecting GPIO 17 to 3.3V"
echo ""
echo "4. Check logs: tail -f /var/www/gsmdialler-data/log.txt"
echo ""

