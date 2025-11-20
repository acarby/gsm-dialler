# Quick Test: GPIO 17 Right Now

## ✅ Current Status
- **Your reading of 0V is CORRECT!** This means GPIO 17 is LOW (idle, not triggered)
- The monitoring script is running and active
- Boot delay has completed (started at 13:41:27)

## 🧪 Test It Now - Trigger GPIO 17 HIGH

### Method 1: Quick Manual Test (Safest)
1. **Keep multimeter connected:**
   - Black probe → GND terminal
   - Red probe → "1017" terminal (GPIO 17)

2. **Temporarily connect GPIO 17 to 3.3V:**
   - Get a small wire or jumper
   - **Momentarily** touch one end to **"+3V3"** terminal (pink LED)
   - **Momentarily** touch the other end to **"1017"** terminal
   - **Watch your multimeter** - it should jump to ~3.3V
   - **Watch the LED** - light blue LED next to "1017" should light up

3. **What should happen:**
   - Multimeter shows ~3.3V
   - Light blue LED turns ON
   - Alarm triggers (check log file)

4. **Disconnect immediately** after testing

### Method 2: Using a Switch/Button (Better)
If you have a momentary switch or button:
- Connect one side to "+3V3" terminal
- Connect other side to "1017" terminal
- Press button → GPIO 17 goes HIGH → Alarm triggers
- Release button → GPIO 17 goes LOW → Back to idle

## 📊 Expected Readings
| State | Voltage | LED | Meaning |
|-------|---------|-----|---------|
| **Idle (LOW)** | **0V** ✅ (what you're seeing) | OFF | No alarm, waiting |
| **Triggered (HIGH)** | **3.3V** | ON | Alarm detected! |

## 🔍 Verify It Worked
After triggering HIGH, check:
```bash
tail -5 /var/www/gsmdialler-data/log.txt
```
You should see: `Fire Alarm Trigger`

## ⚠️ Important Notes
- **0V = Normal idle state** - This is correct!
- GPIO 17 only goes HIGH (3.3V) when triggered
- The script is monitoring and will trigger calls when it detects HIGH
- Boot delay prevents false triggers during startup



