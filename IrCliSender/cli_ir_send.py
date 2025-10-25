# ==============================================================================
# Panasonic HK9327K IR Remote Controller CLI Sender
# ==============================================================================
# This script reads pre-recorded IR RAW timing data from a CSV file and sends 
# the corresponding signal to an Arduino Uno over a serial port.
# The Arduino, running the 'ArdUnoPrj_IrSendFromPython.ino' sketch, then 
# transmits the signal via an IR LED connected to pin D3, allowing control of 
# Panasonic lighting fixtures via the command line.
#
# Prerequisite:
#   - Arduino must be connected and running the ArdUnoPrj_IrSendFromPython.ino sketch.
#   - pyserial library must be installed (pip install pyserial).
#   - The 'panasonic_hk9327k_signals.csv' file must be present in the same directory.
#
# Usage (Command Line Interface):
#   python cli_ir_send.py <channel> <button>
#
# Arguments:
#   <channel> : The lighting channel (e.g., ch1, ch2, ch3).
#   <button>  : The command button (e.g., full, fav, night, up, down, off).
#
# Example (Turn on channel 2 lights fully):
#   python cli_ir_send.py ch2 full
#
# Example (Dim down channel 3 lights):
#   python cli_ir_send.py ch3 down
#
# Serial Protocol Format (Sent to Arduino):
#   RAW:<length>:<t1>,<t2>,<t3>,...
#
# ==============================================================================

import serial
import csv
import sys
import time
from typing import Dict, Any, Optional

# === Configuration ===
PORT = 'COM3'
BAUD = 115200
CSV_FILE = 'panasonic_hk9327k_signals.csv'
# Waiting time (in ms) for Arduino to process the command after sending
WAIT_FOR_ARDUINO_MS = 100 

# === Functions ===
def get_raw_timings(channel: str, button: str) -> Optional[str]:
    """Load the CSV file and search for the raw timings for a specific channel and button."""
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if row['channel'] == channel and row['button'] == button:
                    # raw_timings format: t1,t2,t3,...
                    return row['raw_timings']
        
        print(f"ERROR: Code not found for Channel: {channel}, Button: {button}")
        return None
        
    except FileNotFoundError:
        print(f"ERROR: CSV file not found at {CSV_FILE}")
        return None
    except Exception as e:
        print(f"ERROR reading CSV: {e}")
        return None

def send_ir_signal(raw_timings_str: str) -> None:
    """Send the RAW timing data to the Arduino via serial."""
    try:
        # Connect to Arduino
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2) # Wait for Arduino to fully initialize after connection
        
        # Clear the serial buffer of any old data (like the setup message)
        ser.reset_input_buffer()
        
        # Calculate length (number of comma-separated values)
        length = raw_timings_str.count(',') + 1
        
        # Format the command string for the Arduino sketch
        command_string = f"RAW:{length}:{raw_timings_str}\n"
        
        print(f"Sending command to Arduino: {command_string.strip()}")
        
        # Send the command string
        ser.write(command_string.encode('ascii'))
        
        # Wait for Arduino to process and send the signal
        time.sleep(WAIT_FOR_ARDUINO_MS / 1000.0)
        
        # Read the confirmation response from Arduino
        response = ser.readline().decode('ascii').strip()
        
        if response.startswith("SENT:"):
            print(f"✅ SUCCESS: Signal sent. Arduino response: {response}")
        else:
            # Enhanced error handling for unexpected response
            print(f"⚠️ WARNING: Arduino did not return expected confirmation 'SENT:'.")
            print(f"           Received: '{response}'")
            print(f"           (The signal may have been sent successfully regardless.)")
            
    except serial.SerialException as e:
        print(f"❌ FATAL ERROR: Could not connect to {PORT}. Is Arduino connected and not in use? ({e})")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

# === Main Execution ===
if __name__ == "__main__":
    
    # Check for arguments: script_name <channel> <button>
    if len(sys.argv) != 3:
        print("Usage: python cli_ir_send.py <channel> <button>")
        print("Example: python cli_ir_send.py ch1 full")
        sys.exit(1)

    channel_arg = sys.argv[1].lower()
    button_arg = sys.argv[2].lower()

    # 1. Look up the RAW timings
    raw_data = get_raw_timings(channel_arg, button_arg)

    if raw_data:
        # 2. Send the signal via serial
        send_ir_signal(raw_data)