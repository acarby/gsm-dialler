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
    import sys
    sys.stdout.flush()  # Ensure header is sent immediately

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
        # Try to open serial port with timeout
        try:
            modem = serial.Serial(PORT, BAUD, timeout=2)
        except serial.SerialException as e:
            raise Exception(f"Could not open serial port {PORT}: {e}")
        
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

        # Check SIM status
        modem.write(b"AT+CPIN?\r")
        time.sleep(0.5)
        sim_response = modem.read(100).decode(errors="ignore")
        response_lines.append("AT+CPIN?")
        response_lines.append(sim_response.strip())
        if "READY" not in sim_response:
            raise Exception(f"SIM not ready: {sim_response.strip()}")

        # Check network registration
        modem.write(b"AT+CREG?\r")
        time.sleep(0.5)
        reg_response = modem.read(100).decode(errors="ignore")
        response_lines.append("AT+CREG?")
        response_lines.append(reg_response.strip())

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
        # Clear any existing data first
        modem.reset_input_buffer()
        start_time = time.time()
        prompt_received = False
        prompt_wait_time = 5  # Wait up to 5 seconds for prompt
        
        while time.time() - start_time < prompt_wait_time:
            if modem.in_waiting > 0:
                response = modem.read(modem.in_waiting).decode(errors="ignore")
                if response:
                    response_lines.append(f"Prompt wait: {response.strip()}")
                    if ">" in response:
                        prompt_received = True
                        break
            time.sleep(0.2)
        
        if not prompt_received:
            # Try reading one more time
            time.sleep(0.5)
            if modem.in_waiting > 0:
                response = modem.read(modem.in_waiting).decode(errors="ignore")
                if response:
                    response_lines.append(f"Final read: {response.strip()}")
                    if ">" in response:
                        prompt_received = True

        # Send the message - handle special characters and newlines
        # Many modems prefer single-line SMS without special formatting
        message_clean = message.strip()
        
        # Replace newlines with spaces for better compatibility
        message_clean = message_clean.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        # Clean up multiple spaces
        message_clean = ' '.join(message_clean.split())
        
        # Limit message length (SMS max is 160 chars for single message)
        if len(message_clean) > 160:
            message_clean = message_clean[:157] + "..."
            response_lines.append(f"⚠️ Message truncated to 160 chars")
        
        # Send message - use UTF-8 encoding
        # Send message text first
        modem.write(message_clean.encode('utf-8'))
        time.sleep(0.2)  # Small delay before Ctrl+Z
        
        # Send Ctrl+Z to terminate message
        modem.write(b'\x1A')
        response_lines.append(f"Message sent ({len(message_clean)} chars): {message_clean[:50]}...")
        time.sleep(2)  # Give modem time to process and respond

        # Monitor for SMS send confirmation
        start_time = time.time()
        sms_sent = False
        error_occurred = False
        last_response_time = start_time

        while time.time() - start_time < SMS_TIMEOUT:
            # Read all available data
            if modem.in_waiting > 0:
                data = modem.read(modem.in_waiting).decode(errors="ignore")
                if data:
                    # Split into lines
                    for line in data.split('\n'):
                        line = line.strip()
                        if line:
                            response_lines.append(line)
                            last_response_time = time.time()

                            # Check for success indicators
                            if "+CMGS:" in line:
                                sms_sent = True
                                response_lines.append("✓ SMS send confirmed via +CMGS")
                                break
                            
                            # Check for OK (but only if we haven't seen an error recently)
                            if line == "OK" and not error_occurred:
                                # Wait a bit more to see if we get +CMGS
                                time.sleep(0.5)
                                if modem.in_waiting > 0:
                                    more_data = modem.read(modem.in_waiting).decode(errors="ignore")
                                    if more_data:
                                        for more_line in more_data.split('\n'):
                                            more_line = more_line.strip()
                                            if more_line:
                                                response_lines.append(more_line)
                                                if "+CMGS:" in more_line:
                                                    sms_sent = True
                                                    break
                                if not sms_sent:
                                    # OK without +CMGS might still be success
                                    sms_sent = True
                                    response_lines.append("✓ SMS send confirmed via OK")
                                break

                            # Check for errors
                            if "ERROR" in line or "CMS ERROR" in line or "+CMS ERROR" in line:
                                error_occurred = True
                                entry["error"] = line
                                # Try to get error code if available
                                if "+CMS ERROR" in line:
                                    entry["error_code"] = line
                                break
                
                if sms_sent or error_occurred:
                    break
            
            # If no response for a while, check if we should timeout
            if time.time() - last_response_time > 10 and last_response_time > start_time:
                response_lines.append("! No response from modem for 10 seconds")
                break
                
            time.sleep(0.2)

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
        import traceback
        entry["traceback"] = traceback.format_exc()

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

