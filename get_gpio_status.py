#!/usr/bin/env python3
"""Simple script to read GPIO17 status - can be called from web server"""
import sys
import json
import os

GPIO_PIN = 17

# Try sysfs first (if GPIO is exported)
sysfs_path = f"/sys/class/gpio/gpio{GPIO_PIN}/value"

try:
    if os.path.exists(sysfs_path):
        # Read from sysfs
        with open(sysfs_path, 'r') as f:
            value = int(f.read().strip())
    else:
        # Fallback: Use RPi.GPIO (may fail if GPIO is busy)
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # Don't setup if already in use, just try to read
        try:
            value = GPIO.input(GPIO_PIN)
        except:
            # If that fails, try setting it up
            GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            value = GPIO.input(GPIO_PIN)
    
    is_high = (value == 1)
    # Wiring: 3.3V → NC (Normally Closed), GPIO17 → C, PUD_DOWN
    # Normal: NC closed → GPIO HIGH (connected to 3.3V)
    # Alarm: NC opens → GPIO LOW (pulled down)
    is_alarm = not is_high  # LOW = alarm (NC open), HIGH = normal

    result = {
        "status": "success",
        "gpio_pin": GPIO_PIN,
        "value": int(value),
        "state": "HIGH" if is_high else "LOW",
        "is_alarm": is_alarm,
        "status_text": "ALARM - NC Open" if is_alarm else "NORMAL - NC Closed (3.3V)",
        "status_class": "danger" if is_alarm else "success"
    }
    
    print(json.dumps(result))
    sys.exit(0)
    
except Exception as e:
    result = {
        "status": "error",
        "error": str(e)
    }
    print(json.dumps(result))
    sys.exit(1)

