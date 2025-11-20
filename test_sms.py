#!/usr/bin/env python3
import os, serial, time, json, sys
from datetime import datetime

# CONFIGURATION
CALL_LIST     = "/var/www/gsmdialler-data/call_list.txt"
MESSAGE_FILE  = "/var/www/gsmdialler-data/message.txt"
LOG_FILE      = "/var/www/gsmdialler-data/log.txt"
PORT          = "/dev/serial0"
BAUD          = 115200
SMS_TIMEOUT   = 30  # seconds to wait max for SMS to send
PAUSE_BETWEEN = 2   # pause between SMS (in seconds)

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

# Step 2: Load message
try:
    with open(MESSAGE_FILE) as f:
        message = f.read().strip()
    if not message:
        abort("Message is empty.")
except Exception as e:
    abort(f"Could not read message: {e}")

results = []

# Step 3: Loop over each number and send SMS
for num in numbers:
    entry = {"number": num}
    response_lines = []
    
    # Log the SMS attempt
    log_event(f"SMS sent to: {num}")

    try:
        modem = serial.Serial(PORT, BAUD, timeout=2)
        time.sleep(1)
        modem.reset_input_buffer()

        # AT test
        modem.write(b"AT\r")
        time.sleep(0.5)
        response = modem.read(100).decode(errors="ignore")
        if "OK" not in response:
            raise Exception("Modem not responding to AT command")
        response_lines.append("AT")
        response_lines.append(response.strip())

        # Set SMS to text mode
        modem.write(b"AT+CMGF=1\r")
        time.sleep(0.5)
        response = modem.read(100).decode(errors="ignore")
        response_lines.append("AT+CMGF=1")
        response_lines.append(response.strip())
        if "OK" not in response:
            raise Exception("Failed to set SMS text mode")

        # Set SMS character set to GSM (optional, but recommended)
        modem.write(b"AT+CSCS=\"GSM\"\r")
        time.sleep(0.3)
        response = modem.read(100).decode(errors="ignore")
        response_lines.append("AT+CSCS=\"GSM\"")
        response_lines.append(response.strip())

        # Send SMS command
        sms_command = f'AT+CMGS="{num}"\r'
        modem.write(sms_command.encode())
        time.sleep(0.5)
        response_lines.append(f"> {sms_command.strip()}")

        # Wait for "> " prompt (some modems send this)
        start_time = time.time()
        prompt_received = False
        while time.time() - start_time < 3:
            response = modem.read(100).decode(errors="ignore")
            if response:
                response_lines.append(response.strip())
                if ">" in response or ">" in response_lines[-1]:
                    prompt_received = True
                    break
            time.sleep(0.2)

        # Send the message
        message_to_send = message + "\x1A"  # \x1A is Ctrl+Z (end of message)
        modem.write(message_to_send.encode())
        response_lines.append(f"Message: {message}")
        time.sleep(1)

        # Monitor for SMS send confirmation
        start_time = time.time()
        sms_sent = False
        error_occurred = False

        while time.time() - start_time < SMS_TIMEOUT:
            line = modem.readline().decode(errors="ignore").strip()
            if line:
                response_lines.append(line)

                # Check for success
                if "+CMGS:" in line or "OK" in line:
                    # Check if we already got an error
                    if not any("ERROR" in l or "CMS ERROR" in l for l in response_lines[-5:]):
                        sms_sent = True
                        break

                # Check for errors
                if "ERROR" in line or "CMS ERROR" in line or "+CMS ERROR" in line:
                    error_occurred = True
                    entry["error"] = line
                    break

            time.sleep(0.3)

        if error_occurred:
            entry["status"] = "error"
        elif sms_sent:
            entry["status"] = "completed"
        else:
            entry["status"] = "timeout"
            entry["error"] = "No confirmation received within timeout period"

        entry["duration_s"] = int(time.time() - start_time)
        entry["log"] = response_lines

    except Exception as e:
        entry["status"] = "error"
        entry["error"] = str(e)
        if response_lines:
            entry["log"] = response_lines

    finally:
        try:
            if 'modem' in locals() and modem.is_open:
                modem.close()
        except:
            pass

    results.append(entry)
    time.sleep(PAUSE_BETWEEN)

# Step 4: Output results as JSON
output = json.dumps({"sms_messages": results, "message": message}, indent=2)
if IS_HTTP:
    print(output)

