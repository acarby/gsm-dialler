#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import os
import signal
import sys
from datetime import datetime

GPIO.setwarnings(False)         # Disable warning on reuse
GPIO.cleanup(17)                # Clean up pin 17 if previously used

GPIO_PIN = 17  # ✅ Use BCM pin 17 (was previously working)
LOG_FILE = "/var/www/gsmdialler-data/log.txt"

# 🔁 Graceful exit handler
def cleanup(signal_received=None, frame=None):
	print("Exiting and cleaning up GPIO.")
	GPIO.cleanup()
	sys.exit(0)

# 📝 Log function
def log_event(message):
	try:
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		with open(LOG_FILE, "a") as log:
			log.write(f"[{timestamp}] {message}\n")
	except Exception as e:
		print(f"⚠️ Failed to write log: {e}")

# 🧠 Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 📡 Handle CTRL+C or kill signal
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# ⏰ Boot delay to ignore modem power-on signal
BOOT_DELAY = 15  # seconds to wait after boot before monitoring
print(f"⏳ Waiting {BOOT_DELAY} seconds for system boot to complete...")
log_event(f"GPIO Trigger starting - boot delay {BOOT_DELAY}s")
time.sleep(BOOT_DELAY)
print("🟢 Waiting for alarm signal... (CTRL+C to stop)")
log_event("GPIO Trigger active - monitoring for alarms")

already_triggered = False

try:
	while True:
		if GPIO.input(GPIO_PIN) == GPIO.HIGH and not already_triggered:
			print("🔥 Alarm detected! Running GSM script...")
			log_event("Fire alarm triggered.")
			already_triggered = True
			# Make calls using call list from GUI
			# Redirect output to log file so we can see what happens
			os.system("python3 /var/www/html/test_call.py >> /var/www/gsmdialler-data/log.txt 2>&1 &")
			# Also send SMS using call list and message from GUI
			os.system("python3 /var/www/html/test_sms.py >> /var/www/gsmdialler-data/log.txt 2>&1 &")
		elif GPIO.input(GPIO_PIN) == GPIO.LOW:
			already_triggered = False
		time.sleep(0.1)
except Exception as e:
	print(f"⚠️ Error: {e}")
	log_event(f"GPIO Trigger Error: {e}")
finally:
	cleanup()
