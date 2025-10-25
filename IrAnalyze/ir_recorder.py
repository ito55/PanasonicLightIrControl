import serial
import re
import csv
import time
from typing import List, Dict, Optional, Any

# === 設定 ===
PORT = 'COM3'  # Arduino serial port
BAUD = 115200
# Expected number of bits for the Panasonic code
MAX_BITS = 40
# Pulse Distance Modulation (PDM) decoding threshold in us. 
# Space times are ~400us (0) or ~1275us (1). 850us is the midpoint threshold.
THRESHOLD = 850  
CSV_FILE = 'panasonic_hk9327k_signals.csv'

# Define the channels and buttons as requested
channels: List[str] = ['ch1', 'ch2', 'ch3']
buttons: List[str] = ['full', 'fav', 'night', 'up', 'down', 'off']

# Create the final list of keys to record
keys_to_record: List[Dict[str, str]] = [
    {'channel': ch, 'button': btn} 
    for ch in channels for btn in buttons
]

# CSV headers
CSV_HEADERS = ['channel', 'button', 'protocol', 'bits', 'hex_code', 'raw_timings']

# === 関数 ===
def parse_raw_data(line: str) -> Optional[List[int]]:
    """Extract raw timing data (mark and space) from the serial line."""
    # Expected format: RAW_DATA:<raw_len>:<mark1>,<space1>,<mark2>,<space2>,...
    match = re.match(r"RAW_DATA:\d+:(.*)", line)
    if match:
        # Convert timing string data to a list of integers
        try:
            timings = [int(t) for t in match.group(1).split(',')]
            # Skip the first two elements (Leader Mark and Leader Space)
            # and take the data payload: mark, space, mark, space, ...
            return timings[2:]
        except ValueError:
            return None
    return None

def decode_pulse_distance(data_timings: List[int]) -> List[int]:
    """Decode raw timings using Pulse Distance Modulation (PDM) into a bit array."""
    bits = []
    # data_timings are arranged alternately as mark, space, mark, space, ...
    for i in range(1, len(data_timings), 2):
        # i corresponds to the space time (the duration of the OFF pulse)
        space = data_timings[i]
        
        if len(bits) >= MAX_BITS:
            break
            
        # If space time is longer than the threshold -> logical 1 (long space)
        # If space time is shorter than the threshold -> logical 0 (short space)
        bit = 1 if space > THRESHOLD else 0
        bits.append(bit)
        
    return bits

def bits_to_hex(bits: List[int]) -> str:
    """Convert the bit array to a hexadecimal code (LSB first)."""
    value = 0
    for i, bit in enumerate(bits):
        value |= (bit << i)  # LSB first (Least Significant Bit first)
    # 40 bits is 10 hex digits (40/4 = 10)
    return f"0x{value:0{MAX_BITS//4}X}" 

# === メイン処理 ===
def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=3)
        time.sleep(2)  # Wait for connection stability
        print(f"✅ Serial port {PORT} connected at {BAUD} baud.")
        
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            
            last_hex: Optional[str] = None # Stores the HEX code of the last recorded signal
            
            for key_info in keys_to_record:
                ch = key_info['channel']
                btn = key_info['button']
                
                print("-" * 40)
                # Prompt the user to press the key
                input(f"👉 Press the remote's key 【{ch} - {btn}】 and press Enter to proceed to the next key...")
                
                # Clear the serial buffer to ignore old data
                ser.reset_input_buffer() 
                
                print(f"   Waiting... Please send the IR signal now.")
                
                start_time = time.time()
                received_signal: bool = False
                
                while time.time() - start_time < 10: # Wait for up to 10 seconds
                    line = ser.readline().decode(errors='ignore').strip()
                    if not line:
                        continue

                    if line.startswith("RAW_DATA:"):
                        # Received RAW data
                        data_timings = parse_raw_data(line)
                        if data_timings:
                            bits = decode_pulse_distance(data_timings)
                            hexcode = bits_to_hex(bits)
                            
                            # Redundancy check: Ignore consecutive signals with the same HEX code
                            if hexcode == last_hex:
                                print(f"   ⚠️ Ignoring repeat signal: {hexcode}")
                                continue

                            # Record the new signal
                            print(f"   ✅ Reception complete: CODE={hexcode}")
                            
                            # Write data to CSV
                            row: Dict[str, Any] = {
                                'channel': ch,
                                'button': btn,
                                'protocol': 'PanaLight_PDM',
                                'bits': len(bits),
                                'hex_code': hexcode,
                                # Save the timing data part (the third element after splitting by ':')
                                'raw_timings': line.split(':', 2)[-1] 
                            }
                            writer.writerow(row)
                            f.flush() # Write immediately to disk
                            
                            last_hex = hexcode
                            received_signal = True
                            break # Move to the next key
                            
                    # Optionally handle fully decoded protocols (PROTOCOL:) here if necessary, 
                    # but the sketch is designed to prioritize RAW data for this remote.
                    
                if not received_signal:
                    print("   ❌ Failed to receive signal within the time limit.")

        print("\n\n=== Recording Complete ===")
        print(f"Signal data saved to {CSV_FILE}.")

    except serial.SerialException as e:
        print(f"\n❌ Serial Communication Error: {e}")
        print(f"Check if port {PORT} is open and if the Arduino is connected.")

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()