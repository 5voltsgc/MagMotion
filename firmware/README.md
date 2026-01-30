# Firmware (Teensy 4.1)

## Overview
Teensy 4.1 firmware that reads analog sensors and streams CSV data over serial.

## Setup

### Install Tools
1. **Arduino IDE:** https://www.arduino.cc/en/software
2. **Teensyduino:** https://www.pjrc.com/teensy/teensyduino.html
   - Install as an add-on to Arduino IDE
   - Follow the installer to select **Teensy 4.1** board support

### Upload to Teensy 4.1
1. Connect Teensy 4.1 to USB
2. Open `MagMotion.ino` in Arduino IDE
3. **Tools → Board → Teensy 4.1**
4. **Tools → Port** → Select your Teensy
5. Click **Upload** (or `Ctrl+U`)

## Configuration
Edit these lines in `MagMotion.ino`:

```cpp
const int NUM_CHANNELS = 4;        // How many sensors
const int UPDATE_MS = 50;          // Send data every 50ms
const int ANALOG_PINS[4] = {A0, A1, A2, A3};  // Which pins to read
```

## Serial Protocol

- **Baud Rate:** 115200
- **Format:**
  ```
  Header:  ch0,ch1,ch2,ch3
  Data:    1000,2500,3200,1800
  Data:    1005,2510,3210,1805
  ...
  ```
- **Range:** 0–4095 (12-bit ADC)

## Testing

1. Upload firmware
2. Open Arduino IDE **Tools → Serial Monitor**
3. Set baud to **115200**
4. You should see CSV rows streaming

## Next Steps
- Add onboard LED status indicator
- Implement command interface (e.g., change update rate via serial)
- Add motion control outputs (PWM to motor drivers)

