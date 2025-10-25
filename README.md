# 💡 PanasonicLightIrControl

[日本語](./README.ja.md) | English

This repository serves as an **integrated project for various Infrared (IR) control systems** targeting Panasonic lighting fixtures (compliant with the HK9327K remote control standard).

It manages systems for IR signal transmission and analysis across different hardware environments, such as a Windows CLI tool, standalone Arduino sketches, and M5Stack devices, using a **monorepo** structure.

---

## 📁 Data (Shared Data)

The `/Data` folder contains static assets and data utilized across the entire project.

| File / Folder | Description | Purpose |
| :--- | :--- | :--- |
| `panasonic_hk9327k_signals.csv` | **IR RAW Timing Data (Master)** | Stores RAW timing data corresponding to each button on the remote control. |
| `HK9327K.jpg` | **Remote Control Image** | An image of the target remote control (HK9327K). |

---

## 🛠️ Systems

The following systems are currently developed and maintained in this repository. For detailed setup instructions, usage, and operating environments, please refer to the `README.md` file within each folder.

### 1. [IrCliSender (Windows CLI Sender System)](./IrCliSender/README.md)

| Overview | A system designed to send IR signals from a Windows PC command line via an Arduino Uno. Primarily used for routine lighting operation control from a PC. |
| :--- | :--- |
| **Structure** | Python script (`cli_ir_send.py`) and Arduino Sketch (`IrCliSender.ino`) |
| **Objective** | Transmits the IR signal corresponding to the configured channel and button. |

### 2. [IrAnalyze (IR Data Analysis System)](./IrAnalyze/README.md)

| Overview | A system for capturing and analyzing IR signals from the Panasonic HK9327K remote. Used for adding and verifying new remote signals. |
| :--- | :--- |
| **Structure** | Includes Arduino Sketch and auxiliary Python scripts for analysis. |
| **Objective** | Acquires and displays RAW data of signals received by an IR receiver, providing foundational information for updating the shared CSV data. |

---

## 🚀 Get Started

Cloning the Git repository can be performed using standard operations; no special procedures are required.

```bash
git clone https://github.com/ito55/PanasonicLightIrControl.git
cd PanasonicLightIrControl