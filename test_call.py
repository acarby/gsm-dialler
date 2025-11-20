#!/usr/bin/env python3
import os, serial, time, json, sys
from datetime import datetime

# CONFIGURATION
CALL_LIST     = "/var/www/gsmdialler-data/call_list.txt"
LOG_FILE      = "/var/www/gsmdialler-data/log.txt"
PORT          = "/dev/serial0"
BAUD          = 115200
CALL_TIMEOUT  = 40  # seconds to wait max for call to end
PAUSE_BETWEEN = 1   # pause between calls (in seconds)

# Detect if running from HTTP (CGI) or command line
IS_HTTP = os.environ.get('REQUEST_METHOD') is not None

# Only print Content-Type header if running via HTTP
if IS_HTTP:
    print("Content-Type: application/json\n")

def log_event(message):
    """Log an event to the log file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as log:
            log.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"⚠️ Failed to write log: {e}", file=sys.stderr)

def abort(msg):
    error_msg = json.dumps({"status": "error", "error": msg})
    if IS_HTTP:
        print(error_msg)
    sys.exit(1)

# Step 1: Load call list
try:
    with open(CALL_LIST) as f:
        numbers = [line.strip() for line in f if line.strip()]
    if not numbers:
        abort("Call list is empty.")
except Exception as e:
    abort(f"Could not read call list: {e}")

results = []

# Step 2: Loop over each number
for num in numbers:
    entry = {"number": num}
    response_lines = []
    
    # Log the call attempt
    log_event(f"Call made to: {num}")

    try:
        modem = serial.Serial(PORT, BAUD, timeout=0.2)
        time.sleep(1)
        modem.reset_input_buffer()

        # AT test
        modem.write(b"AT\r")
        time.sleep(0.5)

        # Dial the number
        at_command = f"ATD{num};\r"
        modem.write(at_command.encode())
        response_lines.append(f"> {at_command.strip()}")
        time.sleep(1)

        # Monitor for call progress
        start_time = time.time()
        call_done = False

        while time.time() - start_time < CALL_TIMEOUT:
            line = modem.readline().decode(errors="ignore").strip()
            if line:
                response_lines.append(line)

                # Check for known end indicators
                if ("NO CARRIER" in line or
                    "VOICE CALL: END" in line or
                    "+CLCC: 1,0,6" in line or  # call ended
                    "BUSY" in line or
                    "NO ANSWER" in line):
                    call_done = True
                    break
            time.sleep(0.2)

        if not call_done:
            # Try to hang up if timeout occurs
            modem.write(b"ATH\r")
            time.sleep(0.5)
            response_lines.append("! Timeout - Hangup sent")
            entry["status"] = "timeout"
        else:
            entry["status"] = "completed"

        entry["duration_s"] = int(time.time() - start_time)
        entry["log"] = response_lines

    except Exception as e:
        entry["status"] = "error"
        entry["error"] = str(e)

    finally:
        if modem and modem.is_open:
            modem.close()

    results.append(entry)
    time.sleep(PAUSE_BETWEEN)

# Step 3: Output results as JSON
output = json.dumps({"calls": results}, indent=2)
if IS_HTTP:
    print(output)
