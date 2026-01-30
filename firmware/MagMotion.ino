// MagMotion Firmware - Teensy 4.1
// Real-time sensor monitoring and motion control
// 
// Serial Output: ASCII rows (CSV or plain numbers)
// Baud: 115200
// Example output: "1000,2500,3200,1800" (4 sensor channels)

// ========== USER CONFIG ==========
const int BAUD_RATE = 115200;
const int NUM_CHANNELS = 4;  // Number of analog inputs to read
const int UPDATE_MS = 50;    // Update interval (milliseconds)
const int ANALOG_PINS[4] = {A0, A1, A2, A3};  // Analog pin inputs
// ================================

unsigned long last_update = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  delay(1000);  // Wait for serial monitor to attach
  
  Serial.println("MagMotion Firmware v1.0");
  Serial.println("Teensy 4.1 - Sensor Monitor");
  Serial.println("Ready. Sending data...");
  Serial.println();
  
  // Send header row
  Serial.print("ch0");
  for (int i = 1; i < NUM_CHANNELS; i++) {
    Serial.print(",ch");
    Serial.print(i);
  }
  Serial.println();
}

void loop() {
  unsigned long now = millis();
  
  if (now - last_update >= UPDATE_MS) {
    last_update = now;
    
    // Read all analog channels
    for (int i = 0; i < NUM_CHANNELS; i++) {
      int value = analogRead(ANALOG_PINS[i]);
      Serial.print(value);
      
      if (i < NUM_CHANNELS - 1) {
        Serial.print(",");
      }
    }
    Serial.println();
  }
}
