#!/usr/bin/env python3
"""
Test script to verify GPIO17 connection to fire alarm panel
Shows current state and monitors for changes
"""
import RPi.GPIO as GPIO
import time
import sys

GPIO_PIN = 17

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_state_name(state):
    """Convert GPIO state to readable name"""
    if state == GPIO.HIGH:
        return "HIGH (Normal - Relay OPEN)"
    else:
        return "LOW (Alarm - Relay CLOSED)"

print("=" * 60)
print("GPIO17 Connection Test")
print("=" * 60)
print(f"\nWiring:")
print(f"  GPIO17 (Pin 11) → Eurofire NO (Normally Open)")
print(f"  GND (Pin 9/14)  → Eurofire COM (Common)")
print(f"\nExpected behavior:")
print(f"  Normal state: GPIO17 = HIGH (relay open, pulled up)")
print(f"  Alarm state:  GPIO17 = LOW (relay closed, connected to GND)")
print("=" * 60)

# Read current state
current_state = GPIO.input(GPIO_PIN)
print(f"\n📊 Current GPIO17 state: {get_state_name(current_state)}")
print(f"   Raw value: {current_state} ({'HIGH' if current_state else 'LOW'})")

# Ask if user wants to monitor
print("\n" + "=" * 60)
response = input("Monitor for changes? (y/n): ").strip().lower()

if response == 'y':
    print("\n🟢 Monitoring GPIO17... (Press CTRL+C to stop)")
    print("   Change the relay state on your panel to test")
    print("   (Close relay = Alarm, Open relay = Normal)\n")
    
    last_state = current_state
    change_count = 0
    
    try:
        while True:
            state = GPIO.input(GPIO_PIN)
            
            # Detect state change
            if state != last_state:
                change_count += 1
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] ⚡ STATE CHANGED!")
                print(f"   From: {get_state_name(last_state)}")
                print(f"   To:   {get_state_name(state)}")
                print(f"   Changes detected: {change_count}\n")
                last_state = state
            else:
                # Show current state every 5 seconds
                if int(time.time()) % 5 == 0:
                    print(f"[{time.strftime('%H:%M:%S')}] State: {get_state_name(state)}", end='\r')
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")
        print(f"   Total state changes detected: {change_count}")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)

GPIO.cleanup()

