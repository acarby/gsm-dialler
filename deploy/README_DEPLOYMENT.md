# GSM Dialler Deployment Guide

This package contains everything needed to deploy the GSM Dialler system on a fresh Raspberry Pi.

## 📦 Package Contents

- `install.sh` - Automated installation script
- All source files (PHP, Python scripts)
- Systemd service files
- Documentation

## 🚀 Quick Deployment

### Option 1: Automated Installation (Recommended)

1. **Copy the entire `gsm-dialler` folder to the target Raspberry Pi:**
   ```bash
   scp -r gsm-dialler pi@raspberrypi.local:~/
   ```

2. **SSH into the target Pi:**
   ```bash
   ssh pi@raspberrypi.local
   ```

3. **Run the installation script:**
   ```bash
   cd ~/gsm-dialler/deploy
   sudo bash install.sh
   ```

4. **Access the web interface:**
   - Open browser to: `http://raspberrypi.local/login.php`
   - Username: `admin`
   - Password: `dialler123`

### Option 2: Manual Installation

If you prefer manual installation, follow these steps:

1. **Install dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y apache2 php libapache2-mod-php python3 python3-pip python3-rpi.gpio python3-serial
   sudo pip3 install pyserial RPi.GPIO gpiozero
   ```

2. **Copy files:**
   ```bash
   sudo cp *.php /var/www/html/
   sudo cp test_*.py /var/www/html/
   sudo cp gpio_trigger.py /var/www/html/
   sudo cp power_on_modem.py /usr/local/bin/
   ```

3. **Set permissions:**
   ```bash
   sudo chown -R www-data:www-data /var/www/html
   sudo chmod +x /var/www/html/*.py
   sudo mkdir -p /var/www/gsmdialler-data
   sudo chown -R www-data:www-data /var/www/gsmdialler-data
   ```

4. **Configure services:**
   ```bash
   sudo cp modem-power.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable modem-power.service
   sudo systemctl start modem-power.service
   ```

## 🔧 System Requirements

- **Hardware:**
  - Raspberry Pi (any model with GPIO)
  - GSM Modem connected to `/dev/serial0`
  - GPIO 17 connected to fire alarm relay

- **Software:**
  - Raspberry Pi OS (Debian-based)
  - Python 3.x
  - Apache2 web server
  - PHP 7.4+

## 📋 Pre-Installation Checklist

Before deploying, ensure:

- [ ] Raspberry Pi OS is installed and updated
- [ ] Network connectivity is working
- [ ] GSM modem is physically connected to serial port
- [ ] GPIO 17 is available (not used by other services)
- [ ] Serial port is available (`/dev/serial0`)

## 🔍 Post-Installation Verification

After installation, verify:

1. **Services are running:**
   ```bash
   sudo systemctl status modem-power.service
   sudo systemctl status gpio-trigger.service
   ```

2. **Web interface is accessible:**
   ```bash
   curl http://localhost/login.php
   ```

3. **Serial port is accessible:**
   ```bash
   ls -l /dev/serial0
   ```

4. **GPIO is working:**
   ```bash
   python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); print('GPIO OK')"
   ```

## 🛠️ Troubleshooting

### Service won't start
```bash
sudo journalctl -u gpio-trigger.service -n 50
```

### Serial port issues
```bash
sudo usermod -a -G dialout pi
sudo usermod -a -G dialout www-data
# Then reboot
```

### Web interface not accessible
```bash
sudo systemctl status apache2
sudo apache2ctl configtest
```

### GPIO permission issues
```bash
sudo usermod -a -G gpio pi
# Then reboot
```

## 📝 Configuration

### Change Web Interface Password

Edit `/var/www/html/login.php` and update the password hash.

### Modify GPIO Pin

Edit `/var/www/html/gpio_trigger.py` and change `GPIO_PIN = 17` to your desired pin.

### Change Serial Port

Edit the scripts and change `PORT = "/dev/serial0"` to your port.

## 🔄 Updating an Existing Installation

To update an existing installation:

1. Backup your data:
   ```bash
   sudo cp -r /var/www/gsmdialler-data ~/backup/
   ```

2. Copy new files:
   ```bash
   sudo cp *.php /var/www/html/
   sudo cp *.py /var/www/html/
   ```

3. Restart services:
   ```bash
   sudo systemctl restart gpio-trigger.service
   ```

## 📞 Support

For issues or questions, check:
- Log file: `/var/www/gsmdialler-data/log.txt`
- Service logs: `sudo journalctl -u gpio-trigger.service`

## 📄 License

[Add your license information here]

