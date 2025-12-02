# GSM Dialler System

## 🔐 Login Credentials

**URL:** http://gsmdialler.local/login.php

- **Username:** `admin`
- **Password:** `dialler123`

---

## 📁 File Structure

### Web Interface Files
- `index.php` - Main dashboard for managing call lists and messages
- `login.php` - Login page (contains credentials)
- `logout.php` - Logout handler
- `auth.php` - Authentication check

### Core Scripts
- `gpio_trigger.py` - Monitors GPIO 17 for alarm signals and triggers calls
- `test_call.py` - Main GSM dialing script that reads numbers and makes calls
- `test_sms.py` - SMS sending script
- `power_on_modem.py` - Powers on GSM modem via GPIO 17
- `test_gpio.py` - **Test script to verify GPIO connection to fire panel**

### Data Directory
- `gsmdialler-data/` - Contains:
  - `call_list.txt` - List of phone numbers to dial (one per line)
  - `message.txt` - Message to send
  - `log.txt` - System logs

### System Service
- `modem-power.service` - Systemd service file for modem power management

---

## 🔧 System Configuration

### Serial Port
- **Port:** `/dev/serial0`
- **Baud Rate:** 115200

### GPIO Configuration
- **GPIO Pin 17:** Used for:
  - Powering on the modem (output)
  - Monitoring alarm signals (input)

**Fire Panel Wiring:**
- GPIO17 (Pin 11) → Eurofire NO (Normally Open)
- GND (Pin 9/14) → Eurofire COM (Common)
- **Pull-up enabled:** Normal = HIGH, Alarm = LOW

### Active Services
- `modem-power.service` - Powers on modem at boot
- `ModemManager` - Manages GSM modem
- `gpio_trigger.py` - Running as background process monitoring GPIO 17

---

## 🧪 Testing GPIO Connection

To test if the GPIO connection to the fire alarm panel is working:

```bash
python3 /home/pi/gsm-dialler/test_gpio.py
```

Or from the web directory:
```bash
python3 /var/www/html/test_gpio.py
```

This script will:
- Show the current GPIO17 state
- Monitor for state changes
- Help verify the wiring is correct

**Expected behavior:**
- **Normal state:** GPIO17 = HIGH (relay open)
- **Alarm state:** GPIO17 = LOW (relay closed, connected to GND)

---

## 📞 How It Works

1. **Alarm Detection:** `gpio_trigger.py` monitors GPIO 17 for LOW signal (relay closed)
2. **Call Trigger:** When alarm detected, it runs `test_call.py` and `test_sms.py`
3. **Dialing:** Script reads numbers from `gsmdialler-data/call_list.txt` and dials each one
4. **SMS:** Script sends SMS to all numbers in call list with message from `gsmdialler-data/message.txt`
5. **Call Management:** Uses AT commands to dial, monitor, and hang up calls

---

## 🚀 Usage

### Web Interface
1. Navigate to http://gsmdialler.local/login.php
2. Login with credentials above
3. Manage call list and messages
4. Test calls and SMS from dashboard

### Manual Call Test
```bash
python3 /var/www/html/test_call.py
```

### Manual SMS Test
```bash
python3 /var/www/html/test_sms.py
```

### Test GPIO Connection
```bash
python3 /home/pi/gsm-dialler/test_gpio.py
```

### Check GPIO Monitor
```bash
python3 /var/www/html/gpio_trigger.py
```

---

## 📝 Notes

- Original files are still in `/var/www/html/` and `/var/www/gsmdialler-data/`
- This folder is a copy for easy access and backup
- To modify the system, edit files in `/var/www/html/` (requires sudo)
- Modem power script logs to `/home/pi/modem_boot.log`
- GPIO trigger uses pull-up resistor: LOW = alarm, HIGH = normal
