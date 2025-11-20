# GPIO 17 Testing Guide

## ⚠️ IMPORTANT SAFETY WARNING
- **Raspberry Pi GPIO pins are 3.3V logic, NOT 5V**
- **NEVER apply 5V directly to a GPIO pin - it will damage your Pi!**
- Maximum safe voltage: 3.3V

## GPIO Screw Terminal HAT (EP0129)
You're using the **52Pi GPIO Screw Terminal HAT (SKU: EP-0129)** which provides:
- Screw terminals for each GPIO pin
- LED indicators showing pin status:
  - **Red LEDs** = 5V power pins
  - **Pink LEDs** = 3.3V power pins
  - **Dark blue LEDs** = Special function pins
  - **Light blue LEDs** = Regular GPIO pins (like GPIO 17)

## GPIO 17 Pin Location
- **BCM Pin:** GPIO 17
- **Physical Pin:** Pin 11 (on 40-pin header)
- **Screw Terminal Label:** **"1017"** (on EP0129 HAT)
- **LED Color:** Light blue (regular GPIO)
- **LED Position:** In the "GPIO STATUS" column, next to the "1017" terminal
- **Configuration:** INPUT with pull-down resistor

**On Your HAT:** Look for the screw terminal labeled **"1017"** - this is GPIO 17!

## Testing with Multimeter

### Method 1: Measure Voltage with Multimeter (Safe - Read Only)
**Using EP0129 Screw Terminal HAT:**

**Multimeter Setup (IMPORTANT!):**
1. **Red probe** → Connect to **"VΩmA"** jack (for voltage/resistance measurements)
2. **Black probe** → Connect to **"COM"** jack (common/ground)
3. **Rotary dial** → Set to **DC Voltage** (V with a straight line, not V~)
4. **Display** → Should show "0.000 V" or similar when probes are not touching anything

**⚠️ Common Mistake:** Do NOT use the "10A" jack for voltage measurements - that's only for high current!

**Measuring GPIO 17:**
1. Connect **black probe** to **GND screw terminal** (labeled "GND" on the HAT)
2. Connect **red probe** to **GPIO 17 screw terminal** (labeled **"1017"** on the HAT)
3. **Expected readings:**
   - **LOW (no trigger):** ~0V (0.0V - 0.3V)
   - **HIGH (triggered):** ~3.3V (3.0V - 3.6V)
4. **Visual Check:** The light blue LED next to "1017" in the GPIO STATUS column should be OFF when LOW, ON when HIGH

### Method 2: Test with 3.3V Source (Safe)
**Using EP0129 Screw Terminal HAT:**
To manually trigger GPIO 17 HIGH:
1. Connect a wire from **3.3V screw terminal** (labeled **"+3V3"** - pink LED) to **GPIO 17 screw terminal** (labeled **"1017"** - light blue LED)
2. **Momentarily** connect (or use a switch/button)
3. This should trigger the alarm (after boot delay)
4. **Use a resistor (1kΩ) in series for safety**
5. **Visual Check:** The light blue LED next to "1017" in the GPIO STATUS column should light up when HIGH

### Method 3: Test with External 3.3V Signal
**Using EP0129 Screw Terminal HAT:**
If you have a 3.3V signal source (e.g., alarm system, sensor):
- Connect signal **GND** to **GND screw terminal** (labeled "GND") on the HAT
- Connect signal **output** to **GPIO 17 screw terminal** (labeled **"1017"**)
- Signal should be 0V (LOW) or 3.3V (HIGH)
- **Visual Check:** Light blue LED next to "1017" will indicate HIGH state

## Testing 5V Signals (Requires Voltage Divider)
If you need to test with a 5V signal, use a voltage divider:

```
5V Source → [10kΩ resistor] → GPIO 17
                          ↓
                      [20kΩ resistor] → GND
```

This divides 5V to ~3.3V (5V × 20k/(10k+20k) = 3.33V)

## Current Status
- GPIO 17 is configured as INPUT with pull-down
- Script waits 15 seconds after boot before monitoring
- Triggers when GPIO 17 goes HIGH (3.3V)

## Verification Steps
1. **Locate terminal:** Find the screw terminal labeled **"1017"** on your EP0129 HAT
2. **Check voltage** at "1017" terminal with multimeter (should be ~0V when idle)
3. **Visual check:** Light blue LED next to "1017" in GPIO STATUS column should be OFF when idle
4. **Apply 3.3V** to "1017" terminal (connect from "+3V3" terminal via safe method above)
5. **Visual check:** Light blue LED next to "1017" should turn ON when HIGH
6. **Check log file:** `/var/www/gsmdialler-data/log.txt`
7. Should see "Fire Alarm Trigger" entry

## EP0129 HAT Benefits
- **Easy connections:** Screw terminals make it easy to connect wires
- **Visual feedback:** LED indicators show pin status in real-time
- **Safe testing:** Can easily measure voltage at screw terminals
- **No soldering:** Just tighten screws to make connections

