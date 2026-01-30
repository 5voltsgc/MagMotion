# Python Program

## Overview
Python communication layer and GUI for Teensy 4.1 sensor monitoring.

## Setup

### 1. Create Virtual Environment
```powershell
cd python
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

## Project Structure

- **`main.py`** - Entry point; serial reader placeholder
- **`requirements.txt`** - Python dependencies (pyserial, PyQt5, pyqtgraph)
- **`serial_reader.py`** (future) - Dedicated serial communication module
- **`ui.py`** (future) - PyQtGraph-based real-time plotting

## Key Modules

### `SerialReader` Class
Handles non-blocking reads from Teensy:
- Drains buffer, keeps latest valid row
- Parses CSV headers and numeric data
- Thread-safe design for GUI integration

### Example Usage
```python
from main import SerialReader

reader = SerialReader("/dev/ttyACM0", baud=115200)
labels, values = reader.read_latest()
print(labels)  # ['ch0', 'ch1', 'ch2', 'ch3']
print(values)  # [1000, 2500, 3200, 1800]
reader.close()
```

## Next Steps

1. **Build UI** - Add PyQtGraph bars or line plot
2. **Real-time updates** - QTimer to refresh every 50ms
3. **Port selector** - Dialog to choose Teensy device
4. **Data logging** - Save CSV snapshots

