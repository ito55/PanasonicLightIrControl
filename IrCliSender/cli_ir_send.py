# ==============================================================================
# Panasonic HK9327K IR Remote Controller CLI Sender - Final Version
# ==============================================================================

import serial
import csv
import sys
import time
from typing import Optional, Dict, Tuple

# === Configuration (Constants using SCREAMING_SNAKE_CASE) ===
# NOTE: Update the port name based on your environment (e.g., 'COM3' or '/dev/ttyACM0')
SERIAL_PORT = 'COM3' 
BAUD_RATE = 115200
# NOTE: Assumes the CSV file is copied to the same directory as this script
CSV_FILE_PATH = 'panasonic_hk9327k_signals.csv' 
# Waiting time (in seconds) for Arduino to process the command after sending
ARDUINO_WAIT_TIME_SEC = 0.1 

# === Type Alias for Clarity ===
# Stores both raw_timings and hex_code
IrTimingData = Dict[str, Dict[str, Tuple[str, str]]] # {channel: {button: (raw_timings, hex_code)}}

# === Core Logic Functions ===

def load_ir_data(file_path: str) -> Tuple[Optional[IrTimingData], Optional[str]]:
    """
    Loads IR timing and Hex data from the CSV file and retrieves the version information.
    Assumes CSV headers include 'channel', 'button', 'raw_timings', and 'hex_code'.
    
    Returns: (IrTimingData, version_string)
    """
    ir_data = {}
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            # 1. Read the first line to get version info
            version_line = f.readline().strip()
            
            # 2. Extract version string from comment line
            version_string = version_line[1:].strip() if version_line.startswith('#') else None
            
            # 3. Read data from the second line onwards using DictReader
            reader = csv.DictReader(f)
            
            for row in reader:
                # Expecting columns: 'channel', 'button', 'raw_timings', 'hex_code'
                channel = row['channel'].lower()
                button = row['button'].lower()
                raw_timings = row['raw_timings']
                # Retrieve the pre-decoded Hex code
                hex_code = row['hex_code'] 
                
                if channel not in ir_data:
                    ir_data[channel] = {}
                
                # Store data as a tuple (raw_timings, hex_code)
                ir_data[channel][button] = (raw_timings, hex_code)
                
        return ir_data, version_string
        
    except FileNotFoundError:
        print(f"❌ FATAL ERROR: CSV file not found at {file_path}")
        return None, None
    except KeyError as e:
        # Catch errors if essential columns are missing
        print(f"❌ FATAL ERROR: Missing expected column in CSV: {e}")
        print(f"           Please ensure the CSV includes 'channel', 'button', 'raw_timings', and 'hex_code'.")
        return None, None
    except Exception as e:
        print(f"❌ FATAL ERROR reading CSV: {e}")
        return None, None

def send_ir_signal(raw_timings_str: str) -> None:
    """
    Sends RAW timing data to the Arduino over the serial port.
    Uses 'with' to ensure the serial port is closed after use.
    """
    try:
        # 1. Establish connection using 'with' statement (port closes automatically)
        print(f"Connecting to Arduino at {SERIAL_PORT}...")
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            # Wait for Arduino reset to complete (recommended for robustness)
            time.sleep(2) 
            
            # 2. Clear serial input buffer
            ser.reset_input_buffer()
            
            # 3. Command formatting
            length = raw_timings_str.count(',') + 1
            # Protocol format: RAW:<length>:<t1>,<t2>,<t3>,...\n
            command_string = f"RAW:{length}:{raw_timings_str}\n"
            
            # Print serial command for debugging, without the full raw data
            print(f"Serial command sent: RAW:{length}:... ({length} values)")
            
            # 4. Transmission and waiting
            ser.write(command_string.encode('ascii'))
            
            # Wait for Arduino to complete signal processing
            time.sleep(ARDUINO_WAIT_TIME_SEC)
            
            # 5. Read confirmation response
            response = ser.readline().decode('ascii').strip()
            
            if response.startswith("SENT:"):
                print(f"✅ SUCCESS: Signal sent. Arduino response: {response}")
            else:
                print(f"⚠️ WARNING: Unexpected Arduino response received: '{response}'")
                print(f"           (Signal may have been sent successfully.)")
            
    except serial.SerialException as e:
        # Catch serial-specific errors and provide detailed guidance
        print(f"❌ FATAL ERROR: Could not connect or communicate on {SERIAL_PORT}.")
        print(f"           Details: Is Arduino connected, powered, and not in use by another program? ({e})")

def main():
    """Manages CLI argument processing and the sending workflow."""
    
    # 1. Argument check
    if len(sys.argv) != 3:
        # Dynamically get script name and display usage
        script_name = sys.argv[0].split('/')[-1].split('\\')[-1] 
        print(f"Usage: python {script_name} <channel> <button>")
        print("Example: python cli_ir_send.py ch1 full")
        sys.exit(1)

    channel_arg = sys.argv[1].lower()
    button_arg = sys.argv[2].lower()

    # 2. Load IR data and get version
    all_ir_data, version_id = load_ir_data(CSV_FILE_PATH)
    if all_ir_data is None:
        sys.exit(1) # Exit if CSV loading failed

    if version_id:
        print(f"Loaded IR Data Version: {version_id}")
    else:
        print("⚠️ WARNING: Could not detect version information in the CSV file.")

    # 3. Search for the specific data
    try:
        # Retrieve the tuple (raw_timings, hex_code)
        raw_data, decoded_hex = all_ir_data[channel_arg][button_arg]
    except KeyError:
        print(f"❌ FATAL ERROR: Code not found for Channel: '{channel_arg}', Button: '{button_arg}'")
        sys.exit(1)

    # 4. Output the decoded Hex value
    print(f"Decoded Hex Value: {decoded_hex}")

    # 5. Send the signal
    send_ir_signal(raw_data)

# === Main Execution ===
if __name__ == "__main__":
    main()