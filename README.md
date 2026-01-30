# MagMotion

A dual-program project for real-time sensor monitoring and motion control using Teensy 4.1 microcontroller and Python GUI.

## Project Structure

```
MagMotion/
├── firmware/              # Teensy 4.1 code (Arduino IDE)
│   ├── MagMotion.ino      # Main firmware sketch
│   └── README.md          # Firmware-specific docs
├── python/                # Python communication & GUI
│   ├── requirements.txt    # Python dependencies
│   ├── main.py            # Entry point
│   └── README.md          # Python-specific docs
├── docs/                  # Design docs, protocols, schematics
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Quick Start

### Firmware (Teensy 4.1)
1. Install Arduino IDE and Teensyduino addon
2. Open `firmware/MagMotion.ino` in Arduino IDE
3. Select **Tools → Board → Teensy 4.1**
4. Connect Teensy via USB and **Upload**

### Python Program
1. Install Python 3.8+
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r python/requirements.txt`
5. Run: `python python/main.py`

## Serial Protocol
- Baud: 115200
- Format: CSV rows or plain numbers (firmware sends; Python reads)
- Example: `"ch0,ch1,ch2,ch3"` (header) → `1000,2500,3200,1800` (data rows)

## Development

- **Firmware changes:** Edit `firmware/MagMotion.ino`, compile & upload via Arduino IDE
- **Python changes:** Edit `python/*.py`, restart `main.py`
- **Documentation:** Add design notes to `docs/`

## GitHub Setup

This repo is version-controlled with Git. See [GITHUB.md](.github/GITHUB.md) for account setup and commit workflow.

## License

[Add license here]

## Author

[Your Name]
