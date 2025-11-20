from gpiozero import LED
from time import sleep
from datetime import datetime

modem_power = LED(17)

# Make sure it's LOW before starting
modem_power.off()
sleep(1)

# Pulse HIGH (trigger ON)
modem_power.on()
sleep(2)

# Optional: turn it off again if it's edge-triggered
modem_power.off()

# Log the action
with open("/home/pi/modem_boot.log", "a") as log:
    log.write(f"[{datetime.now()}] Pulsed GPIO 17 to power on modem.\n")
