# 📡 IrCliSender (Windows CLI Sender System)

## 💡 Overview

This project enables control of Panasonic lighting fixtures (HK9327K standard) from the **Windows Command Line Interface (CLI)**. 

The Python script reads pre-recorded IR RAW timing data from a CSV file and sends the corresponding signal to an Arduino Uno over a serial port. The Arduino then physically transmits the signal via an attached IR LED.

## 🛠️ System Components

| File | Description |
| :--- | :--- |
| `cli_ir_send.py` | Python CLI script. Handles argument parsing, CSV data loading, and serial communication. |
| `SerialToIr_ArdSketch.ino` | Arduino sketch. Receives serial commands and executes the IR signal transmission via an IR LED (connected to Pin D3). |
| `panasonic_hk9327k_signals.csv` | IR RAW timing data. The Python script reads this file. |

## 🔌 Prerequisites and Setup

Before running the Python script, ensure the following conditions are met:

1.  **Hardware Connection:**
    * The **Arduino Uno** must be connected to the PC via USB.
    * The **IR LED** must be correctly wired (typically to Digital Pin D3) to the Arduino.

2.  **Arduino Sketch:**
    * The sketch **`SerialToIr_ArdSketch.ino`** must be uploaded and running on the Arduino.
    * **Note:** The `SERIAL_PORT` setting inside `cli_ir_send.py` must be updated to match the Arduino's COM port (e.g., `'COM3'`).

3.  **Python Environment:**
    * The **`pyserial`** library must be installed:
        ```bash
        pip install pyserial
        ```

4.  **Data File:**
    * The data file **`panasonic_hk9327k_signals.csv`** must be present in this same directory.

---

## 🚀 Usage (Command Line)

The script requires two arguments: the lighting channel and the command button.

### Command Format

```bash
python cli_ir_send.py <channel> <button>
```

### Arguments

| Argument | Example Values | Description |
| :--- | :--- | :--- |
| `<channel>` | `ch1`, `ch2`, `ch3` | The target lighting channel. |
| `<button>` | `full`, `fav`, `night`, `up`, `down`, `off` | The command to execute (Ensure the value exists in the CSV). |

### Examples

| Action | Command |
| :--- | :--- |
| Turn on channel 2 lights fully | `python cli_ir_send.py ch2 full` |
| Dim down channel 3 lights | `python cli_ir_send.py ch3 down` |
| Dim up channel 3 lights | `python cli_ir_send.py ch3 up` |

---

## 🔗 Serial Protocol

The Python script communicates with the Arduino using a simple, defined protocol. This is crucial for verifying the corresponding Arduino sketch is compatible.

| Element | Description |
| :--- | :--- |
| **Format** | `RAW:<length>:<t1>,<t2>,<t3>,...\n` |
| **`RAW`** | Command identifier indicating the data is a RAW timing sequence. |
| **`<length>`** | The number of timing values (the count of comma-separated values). |
| **`<t1>,<t2>,...`** | The actual IR timing values (pulses and gaps in microseconds). |
| **`\n`** | A newline character (`\n`) to terminate the command string. |

After successfully sending the signal, the Arduino is expected to return a confirmation message (e.g., `SENT: <timing_count>`) which the Python script waits for.
