# Quick Start Deployment Guide

## 🚀 Fastest Way to Deploy

### Step 1: Create Package on Source Pi
```bash
cd ~/gsm-dialler/deploy
./create-package.sh
```

This creates a tarball in `/tmp/` with timestamp.

### Step 2: Transfer to Target Pi
```bash
# From your computer or source Pi
scp /tmp/gsm-dialler-package-*.tar.gz pi@target-pi.local:~/
```

### Step 3: Install on Target Pi
```bash
# SSH into target Pi
ssh pi@target-pi.local

# Extract and install
cd ~
tar -xzf gsm-dialler-package-*.tar.gz
cd gsm-dialler-package-*/gsm-dialler/deploy
sudo bash install.sh
```

### Step 4: Configure
1. Open browser: `http://target-pi.local/login.php`
2. Login: `admin` / `dialler123`
3. Add phone numbers to call list
4. Set SMS message
5. Test!

## ✅ Verification

After installation, check:
```bash
# Services running
sudo systemctl status modem-power.service
sudo systemctl status gpio-trigger.service

# Web interface
curl http://localhost/login.php

# Logs
tail -f /var/www/gsmdialler-data/log.txt
```

## 🔧 Alternative: Clone from Git (if using version control)

```bash
git clone <your-repo-url> gsm-dialler
cd gsm-dialler/deploy
sudo bash install.sh
```

