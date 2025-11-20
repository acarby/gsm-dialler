# GSM Dialler System

A Raspberry Pi-based fire alarm notification system that automatically makes phone calls and sends SMS messages when a fire alarm is triggered via GPIO.

## 🔥 Features

- **GPIO Monitoring**: Monitors GPIO pin 17 for fire alarm triggers
- **Automatic Calls**: Dials all numbers in call list when alarm is triggered
- **SMS Notifications**: Sends SMS messages to all contacts
- **Web Interface**: Easy-to-use dashboard for managing contacts and messages
- **Systemd Integration**: Runs automatically on boot
- **Comprehensive Logging**: All events logged with timestamps

## 📋 Requirements

- Raspberry Pi (any model with GPIO)
- GSM Modem connected to `/dev/serial0`
- GPIO 17 connected to fire alarm relay
- Raspberry Pi OS (Debian-based)

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url> gsm-dialler
   cd gsm-dialler
   ```

2. **Run the installation script:**
   ```bash
   cd deploy
   sudo bash install.sh
   ```

3. **Access the web interface:**
   - Open browser to: `http://raspberrypi.local/login.php`
   - Username: `admin`
   - Password: `dialler123`

4. **Configure:**
   - Add phone numbers to the call list
   - Set your SMS message
   - Test the system

For detailed deployment instructions, see [deploy/README_DEPLOYMENT.md](deploy/README_DEPLOYMENT.md)

## 📁 Project Structure

```
gsm-dialler/
├── deploy/                 # Deployment scripts and documentation
│   ├── install.sh         # Automated installation script
│   ├── create-package.sh  # Package creation script
│   └── README_DEPLOYMENT.md
├── *.php                  # Web interface files
├── *.py                   # Python scripts
├── *.service              # Systemd service files
└── README.md             # This file
```

## 🔧 Configuration

### GPIO Pin
Default: GPIO 17. To change, edit `gpio_trigger.py`:
```python
GPIO_PIN = 17  # Change to your desired pin
```

### Serial Port
Default: `/dev/serial0`. To change, edit the Python scripts:
```python
PORT = "/dev/serial0"  # Change to your port
```

### Web Interface Password
Edit `login.php` and update the password hash.

## 📞 How It Works

1. **GPIO Monitoring**: `gpio_trigger.py` continuously monitors GPIO 17
2. **Alarm Detection**: When GPIO goes HIGH, alarm is triggered
3. **Call List**: Reads phone numbers from `/var/www/gsmdialler-data/call_list.txt`
4. **Calls**: `test_call.py` dials each number sequentially
5. **SMS**: `test_sms.py` sends SMS to each number
6. **Logging**: All events logged to `/var/www/gsmdialler-data/log.txt`

## 🛠️ Maintenance

### View Logs
```bash
tail -f /var/www/gsmdialler-data/log.txt
```

### Check Service Status
```bash
sudo systemctl status gpio-trigger.service
sudo systemctl status modem-power.service
```

### Restart Services
```bash
sudo systemctl restart gpio-trigger.service
```

### Update System
```bash
cd ~/gsm-dialler
git pull
sudo bash deploy/install.sh
```

## 📝 File Locations

- **Web Interface**: `/var/www/html/`
- **Python Scripts**: `/var/www/html/*.py`
- **Data Directory**: `/var/www/gsmdialler-data/`
- **Service Files**: `/etc/systemd/system/`
- **Logs**: `/var/www/gsmdialler-data/log.txt`

## 🔐 Security Notes

- Change default password in `login.php` before production use
- Consider using HTTPS for web interface
- Restrict network access if possible
- Regularly update system packages

## 🐛 Troubleshooting

See [deploy/README_DEPLOYMENT.md](deploy/README_DEPLOYMENT.md) for detailed troubleshooting guide.

Common issues:
- **Service won't start**: Check logs with `sudo journalctl -u gpio-trigger.service`
- **Serial port issues**: Ensure user is in `dialout` group
- **GPIO permission errors**: Ensure user is in `gpio` group

## 📄 License

[Add your license here]

## 👥 Contributing

[Add contribution guidelines if applicable]

## 📧 Support

For issues or questions, check the log file or service logs.
