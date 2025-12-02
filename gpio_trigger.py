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
STATUS_FILE = "/var/www/gsmdialler-data/gpio_status.json"  # Status file for web interface

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

# 📊 Update status file for web interface
def update_status_file(gpio_value):
	try:
		# WIRING LOGIC (GPIO17 → NC):
		#  - Pi 3.3V -> Panel COM
		#  - Panel NC -> GPIO17
		#  - Internal PUD_UP
		#  Normal: relay closed -> NC connected to COM -> GPIO17 HIGH (connected to 3.3V)
		#  Alarm:  relay open -> NC disconnected from COM -> GPIO17 LOW (pulled down)
		is_high = (gpio_value == GPIO.HIGH)
		is_alarm = not is_high  # LOW means alarm (NC disconnected)
		status_data = {
			"status": "success",
			"gpio_pin": GPIO_PIN,
			"value": int(gpio_value),
			"state": "HIGH" if is_high else "LOW",
			"is_alarm": is_alarm,
			"status_text": "ALARM - Relay Open" if is_alarm else "NORMAL - Relay Closed",
			"status_class": "danger" if is_alarm else "success",
			"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		}
		import json
		with open(STATUS_FILE, "w") as f:
			json.dump(status_data, f)
	except Exception as e:
		print(f"⚠️ Failed to update status file: {e}")

# 🧠 Setup GPIO
# Using PUD_UP because: GPIO17→NC, 3.3V→COM
# Normal (relay closed): GPIO17 connected to 3.3V = HIGH (NC connected to COM)
# Alarm (relay open): GPIO17 pulled LOW (PUD_UP, NC disconnected from COM)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
last_gpio_state = None
last_status_update = 0
status_update_interval = 1.0  # Update status file max once per second
# Force initial status update after boot delay
initial_status_update_done = False
debounce_samples = []  # For debouncing
debounce_window = 15  # Number of samples to check for stable state (increased for better filtering) (reduced for faster response)

# Alarm handling parameters
# With PUD_UP and GPIO→NC: LOW = alarm (NC disconnected from COM), HIGH = normal (NC connected to COM)
alarm_low_started = None   # When LOW (alarm) state started
normal_high_started = None  # When HIGH (normal) state started
alarm_hold_time = 2.0   # seconds GPIO must stay LOW before triggering alarm
alarm_reset_time = 5.0  # seconds GPIO must stay HIGH before re-arming
alarm_cooldown = 60.0   # seconds between alarm runs
last_alarm_time = 0

try:
	while True:
		# Read GPIO state
		gpio_state = GPIO.input(GPIO_PIN)
		
		# Debouncing: collect samples
		debounce_samples.append(gpio_state)
		if len(debounce_samples) > debounce_window:
			debounce_samples.pop(0)
		
		# Determine stable state (require strong majority to avoid flickering)
		stable_state = None
		if len(debounce_samples) >= debounce_window:
			high_count = sum(1 for s in debounce_samples if s == GPIO.HIGH)
			low_count = len(debounce_samples) - high_count
			# Require at least 80% of samples to agree (more strict than 50%)
			threshold = int(debounce_window * 0.8)
			if high_count >= threshold:
				stable_state = GPIO.HIGH
			elif low_count >= threshold:
				stable_state = GPIO.LOW
			# If neither reaches threshold, keep previous stable state (hysteresis)
			if stable_state is None and last_gpio_state is not None:
				stable_state = last_gpio_state
		
		# Debug: Log state changes and potential issues
		if gpio_state == GPIO.HIGH and stable_state == GPIO.LOW:
			print(f"⚠️ Warning: GPIO reads HIGH but debounced to LOW (high_count={high_count}, low_count={low_count})")
		# Log every state change for debugging
		if stable_state is not None and stable_state != last_gpio_state:
			# With NC wiring: HIGH = NORMAL, LOW = ALARM
			state_name = "HIGH (NORMAL)" if stable_state == GPIO.HIGH else "LOW (ALARM)"
			print(f"📊 GPIO state changed to: {state_name}")
		
		# Only update status file if state changed and enough time passed
		current_time = time.time()
		if stable_state is not None and stable_state != last_gpio_state:
			last_gpio_state = stable_state
			# Update status file immediately on state change
			update_status_file(stable_state)
			last_status_update = current_time
		elif current_time - last_status_update >= status_update_interval:
			# Periodic update even if state hasn't changed
			if stable_state is not None:
				update_status_file(stable_state)
			last_status_update = current_time
		# Force initial status update after boot delay
		if not initial_status_update_done and stable_state is not None:
			update_status_file(stable_state)
			initial_status_update_done = True
			last_status_update = current_time
		
		# Use stable state for alarm detection
		if stable_state is not None:
			# With PUD_UP and GPIO→NC: LOW = alarm (NC disconnected from COM), HIGH = normal (NC connected to COM)
			if stable_state == GPIO.LOW:
				# GPIO is LOW = alarm condition (NC disconnected from COM)
				normal_high_started = None  # Reset normal timer
				if alarm_low_started is None:
					alarm_low_started = current_time  # Start tracking how long LOW has been stable
					print(f"🔴 GPIO17 is LOW (alarm) - started tracking at {current_time}")
				# Only trigger if LOW has been held long enough and cooldown expired
				if (
					current_time - alarm_low_started >= alarm_hold_time
					and not already_triggered
					and current_time - last_alarm_time >= alarm_cooldown
				):
					print("🔥 Alarm detected! Running GSM script...")
					log_event("Fire Alarm Trigger")
					already_triggered = True
					last_alarm_time = current_time
					# Make calls using call list from GUI
					os.system("python3 /var/www/html/test_call.py &")
					# Also send SMS using call list and message from GUI
					os.system("python3 /var/www/html/test_sms.py &")
					print("Calls and SMS triggered successfully")
				elif stable_state == GPIO.LOW and already_triggered:
					# Log that we're still in alarm but cooldown active
					if current_time - last_alarm_time < alarm_cooldown:
						remaining = int(alarm_cooldown - (current_time - last_alarm_time))
						if int(current_time) % 10 == 0:  # Log every 10 seconds
							print(f"⏳ Alarm active but cooldown: {remaining}s remaining")
			else:
				# GPIO is HIGH = normal condition (NC connected to COM)
				alarm_low_started = None  # Reset alarm timer
				if normal_high_started is None:
					normal_high_started = current_time  # Start tracking how long HIGH has been stable
				# Require HIGH to be stable for reset (alarm cleared)
				if already_triggered and (current_time - normal_high_started >= alarm_reset_time):
					already_triggered = False
					normal_high_started = None
				elif not already_triggered:
					normal_high_started = None
		
		time.sleep(0.05)  # Faster sampling for better debouncing
except Exception as e:
	print(f"⚠️ Error: {e}")
	log_event(f"GPIO Trigger Error: {e}")
finally:
	cleanup()
