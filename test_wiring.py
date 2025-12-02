#!/usr/bin/env python3
"""
Quick test to verify GPIO17 wiring and relay state.
Run this while gpio_trigger.py is stopped.
"""
import RPi.GPIO as GPIO
import time
import sys

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

print("=" * 60)
print("GPIO17 Wiring Test")
print("=" * 60)
print("\nExpected wiring:")
print("  - Pi 3.3V → Fire Panel COM")
print("  - Pi GPIO17 → Fire Panel NO")
print("  - Pi GND → Fire Panel GND (if needed)")
print("\nExpected behavior:")
print("  - Normal (relay open): GPIO17 = LOW (pulled down)")
print("  - Alarm (relay closed): GPIO17 = HIGH (connected to 3.3V)")
print("=" * 60)

try:
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print("\nReading GPIO17 (10 samples, 0.5s apart):\n")
    
    high_count = 0
    low_count = 0
    
    for i in range(10):
        val = GPIO.input(17)
        state = "HIGH" if val else "LOW"
        meaning = "ALARM (relay closed)" if val else "NORMAL (relay open)"
        
        if val:
            high_count += 1
        else:
            low_count += 1
        
        print(f"  Sample {i+1:2d}: GPIO17 = {val} ({state:4s}) → {meaning}")
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"Summary: HIGH={high_count}/10, LOW={low_count}/10")
    
    if high_count >= 7:
        print("⚠️  GPIO17 is mostly HIGH - Relay appears CLOSED (ALARM state)")
        print("   If this is wrong, check:")
        print("   1. Is the fire panel actually in alarm?")
        print("   2. Is GPIO17 connected to NO (not NC)?")
        print("   3. Is 3.3V connected to COM?")
    elif low_count >= 7:
        print("✅ GPIO17 is mostly LOW - Relay appears OPEN (NORMAL state)")
        print("   This is correct for normal operation.")
    else:
        print("⚠️  GPIO17 is flickering between HIGH and LOW")
        print("   This suggests:")
        print("   1. Loose wiring connection")
        print("   2. Electrical noise")
        print("   3. Relay in intermediate state")
    
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure gpio_trigger.py is stopped first!")
    sys.exit(1)
finally:
    GPIO.cleanup()



