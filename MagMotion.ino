// MagMotion Firmware - Teensy 4.1
// Real-time sensor monitoring and motion control
// 
// Serial Output: ASCII rows (CSV)
// Baud: 115200

#include "TDW_SPI.h"

// ========== USER CONFIG ==========
const int BAUD_RATE = 115200;
const int PIN_MISOA = 41;
const int PIN_MISOB = 40;
const int PIN_MOSI  = 39;
const int PIN_CS    = 37;
const int PIN_SCK   = 38;
const int PIN_ENABLE = 2;   // Stepper enable (HIGH = disabled)
const int UPDATE_MS = 20;   // Read/print interval (ms)  10 starts to get noisey, 20, 50 works
// ================================

const int MAX_SENSORS = 64;
const int BUFFER_SIZE = MAX_SENSORS + 2;
uint16_t data[BUFFER_SIZE];
int numSensors = 0;
unsigned long lastUpdate = 0;

TDW_SPI spi = TDW_SPI(PIN_MOSI, PIN_MISOA, PIN_MISOB, PIN_SCK, PIN_CS);

void setup() {
  Serial.begin(BAUD_RATE);
  delay(1000);  // Wait for serial monitor to attach

  pinMode(PIN_ENABLE, OUTPUT);
  digitalWrite(PIN_ENABLE, HIGH);

  numSensors = spi.getNumberSensors();
}

void loop() {
  if (numSensors <= 0) return;

  unsigned long now = millis();
  if (now - lastUpdate < (unsigned long)UPDATE_MS) return;
  lastUpdate = now;

  int response = spi.getSensorData(data, BUFFER_SIZE);
  if (response > 0 && response <= MAX_SENSORS) {
    for (int i = 0; i < response; i++) {
      Serial.print(data[i + 2]);
      if (i < response - 1) {
        Serial.print(",");
      }
    }
    Serial.println();
  }
}
