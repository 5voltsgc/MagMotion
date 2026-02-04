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
// -------------------------
// DRV8825 + Limits
// -------------------------
const int PIN_ENABLE = 2;
const int PIN_STEP   = 3;
const int PIN_DIR    = 4;
const int PIN_FAULT  = 5;

const int PIN_LIM_F  = 6;   // Front limit (active LOW)
const int PIN_LIM_B  = 7;   // Back limit (active LOW)
// NOTE: IDOD sensors require ~20 seconds of read cycles to become fully functional.
const int UPDATE_MS = 20;   // Read/print interval (ms)  10 starts to get noisey, 20, 50 works
// ================================

// Pulse timing
const uint16_t STEP_PULSE_US = 3;

// Speeds (microsteps/sec)
const uint32_t HOME_STEPS_PER_SEC    = 16000;
const uint32_t RAPID_STEPS_PER_SEC   = 20000;
const uint32_t SCAN_STEPS_PER_SEC    = 12000;   // will also be limited by sensor read + serial output
const uint32_t BACKOFF_STEPS_PER_SEC = 2000;

// Backoff from switch so it un-triggers
const uint32_t BACKOFF_STEPS = 400;
// Debounce: require N consecutive reads
const uint8_t LIMIT_HITS_REQUIRED = 5;
// Safety: max steps to avoid runaway
const uint32_t MAX_HOME_STEPS = 500000;
const uint32_t MAX_SCAN_STEPS = 2000000;

// -------------------------
// Scan settings YOU will tune
// -------------------------
// steps/mm for your stage.
// If: 200 steps/rev * 32 microstep = 6400 microsteps/rev
// pulley 18 teeth * 2mm pitch = 36mm/rev
// => 6400 / 36 = 177.777... steps/mm
const float STEPS_PER_MM = 6400.0f / 36.0f;

// Start/Stop positions relative to "home reference" (defined after homing backoff)
const float START_POS_MM = 5.0f;
const float STOP_POS_MM  = 150.0f;  // Was 120.0f

// Print every N steps (1 = print every step)
const uint16_t PRINT_EVERY_N_STEPS = 1;

const int MAX_SENSORS = 64;
const int BUFFER_SIZE = MAX_SENSORS + 2;
uint16_t data[BUFFER_SIZE];
int numSensors = 0;
unsigned long lastUpdate = 0;

TDW_SPI spi = TDW_SPI(PIN_MOSI, PIN_MISOA, PIN_MISOB, PIN_SCK, PIN_CS);

enum State {
  STATE_IDLE = 0,
  STATE_HOMING,
  STATE_READ,
  STATE_SCAN,
  STATE_FAULT
};

State currentState = STATE_IDLE;
State nextState = STATE_IDLE;
bool configValid = false;
bool homingStarted = false;
bool scanStarted = false;
bool scanComplete = false;
bool pendingScanAfterHome = false;
bool homeValid = false;
bool slowScan = false;
String faultCode = "";
unsigned long lastStepMicros = 0;
uint32_t homingStepsTaken = 0;
uint32_t backoffStepsTaken = 0;
uint8_t limitHits = 0;
bool homingBackoff = false;
bool homingComplete = false;
long currentPosSteps = 0;
long scanStartSteps = 0;
long scanStopSteps = 0;
bool scanToStart = false;
uint32_t scanStepCounter = 0;
uint32_t scanStepsTaken = 0;
bool scanStepOccurred = false;
bool frontDirIsHigh = false; // direction polarity (false = LOW is front)

const int CMD_BUFFER_SIZE = 64;
char cmdBuffer[CMD_BUFFER_SIZE];
int cmdIndex = 0;

void setState(State newState);
void handleState();
void handleSerial();
void readAndPrintSensors();
void setFault(const String &code);
void resetFault();
void startHoming();
bool isHomingComplete();
void startScan();
bool isScanComplete();
void stepPulse();
void stepInDirection(bool dirHigh);
bool dirTowardFront();
bool dirTowardBack();
bool limitFrontActive();
bool limitBackActive();

void setup() {
  Serial.begin(BAUD_RATE);
  delay(1000);  // Wait for serial monitor to attach

  pinMode(PIN_ENABLE, OUTPUT);
  pinMode(PIN_STEP, OUTPUT);
  pinMode(PIN_DIR, OUTPUT);
  pinMode(PIN_FAULT, INPUT_PULLUP);
  pinMode(PIN_LIM_F, INPUT_PULLUP);
  pinMode(PIN_LIM_B, INPUT_PULLUP);
  digitalWrite(PIN_ENABLE, HIGH);
  digitalWrite(PIN_STEP, LOW);
  digitalWrite(PIN_DIR, LOW);

  numSensors = spi.getNumberSensors();
  configValid = (numSensors > 0);
  setState(STATE_IDLE);
}

void loop() {
  handleSerial();
  handleState();
}

void handleSerial() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (cmdIndex == 0) continue;
      cmdBuffer[cmdIndex] = '\0';
      cmdIndex = 0;

      String cmd = String(cmdBuffer);
      cmd.trim();
      cmd.toUpperCase();

      if (cmd == "STOP") {
        setState(STATE_IDLE);
      } else if (cmd == "RESET") {
        resetFault();
        setState(STATE_IDLE);
      } else if (cmd == "HOME") {
        pendingScanAfterHome = false;
        homeValid = false;
        setState(STATE_HOMING);
      } else if (cmd == "READ") {
        setState(STATE_READ);
      } else if (cmd == "SCAN") {
        if (homeValid) {
          setState(STATE_SCAN);
        } else {
          pendingScanAfterHome = true;
          setState(STATE_HOMING);
        }
      } else if (cmd == "SCANSPEED=SLOW") {
        slowScan = true;
      } else if (cmd == "SCANSPEED=FAST") {
        slowScan = false;
      } else if (cmd == "NUMSENS") {
        Serial.print("NUMSENS:");
        Serial.println(numSensors);
      } else if (cmd == "CONFIG") {
        configValid = true;
      } else if (cmd.startsWith("DIRPOL=")) {
        String val = cmd.substring(7);
        val.trim();
        if (val == "1" || val == "HIGH" || val == "FRONT_HIGH") {
          frontDirIsHigh = true;
        } else if (val == "0" || val == "LOW" || val == "FRONT_LOW") {
          frontDirIsHigh = false;
        } else {
          setFault("DIRPOL");
        }
      } else if (cmd == "FAULT") {
        setFault("HOST");
      }
    } else {
      if (cmdIndex < CMD_BUFFER_SIZE - 1) {
        cmdBuffer[cmdIndex++] = c;
      }
    }
  }
}

void handleState() {
  switch (currentState) {
    case STATE_IDLE:
      digitalWrite(PIN_ENABLE, HIGH); // motor disabled
      if (!configValid) {
        // Stay in IDLE until configuration arrives.
      }
      break;
    case STATE_HOMING:
      if (!homingStarted) startHoming();
      if (isHomingComplete()) {
        if (pendingScanAfterHome) {
          pendingScanAfterHome = false;
          setState(STATE_SCAN);
        } else {
          setState(STATE_IDLE);
        }
      }
      break;
    case STATE_READ:
      if (!configValid) {
        setFault("NO_CONFIG");
        break;
      }
      digitalWrite(PIN_ENABLE, HIGH); // motor disabled for manual move
      readAndPrintSensors();
      break;
    case STATE_SCAN:
      if (!configValid) {
        setFault("NO_CONFIG");
        break;
      }
      if (limitBackActive()) {
        setFault("LIM_BACK");
        break;
      }
      if (limitFrontActive()) {
        setFault("LIM_FRONT");
        break;
      }
      if (!scanStarted) startScan();
      if (isScanComplete()) {
        setState(STATE_IDLE);
        break;
      }
      if (scanStepOccurred && (scanStepCounter % PRINT_EVERY_N_STEPS == 0)) {
        readAndPrintSensors();
      }
      break;
    case STATE_FAULT:
      digitalWrite(PIN_ENABLE, HIGH);
      // Remain in fault until RESET command.
      break;
  }
}

void readAndPrintSensors() {
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
  } else {
    setFault("SENSOR");
  }
}

void setState(State newState) {
  currentState = newState;
  homingStarted = false;
  scanStarted = false;
  scanComplete = false;
  homingStepsTaken = 0;
  backoffStepsTaken = 0;
  limitHits = 0;
  homingBackoff = false;
  homingComplete = false;
  scanToStart = false;
  scanStepCounter = 0;
  scanStepsTaken = 0;
  scanStepOccurred = false;
}

void setFault(const String &code) {
  faultCode = code;
  Serial.print("FAULT:");
  Serial.println(faultCode);
  currentState = STATE_FAULT;
}

void resetFault() {
  faultCode = "";
}

void startHoming() {
  homingStarted = true;
  homingComplete = false;
  digitalWrite(PIN_ENABLE, LOW);
  digitalWrite(PIN_DIR, dirTowardFront() ? HIGH : LOW);
  lastStepMicros = micros();
}

bool isHomingComplete() {
  if (homingComplete) return true;

  // Security: fault if back limit is hit during homing
  if (limitBackActive()) {
    setFault("LIM_BACK");
    return false;
  }

  // Phase 1: move toward front limit until debounced hit
  if (!homingBackoff) {
    if (limitFrontActive()) {
      limitHits++;
    } else {
      limitHits = 0;
    }
    if (limitHits >= LIMIT_HITS_REQUIRED) {
      homingBackoff = true;
      backoffStepsTaken = 0;
      digitalWrite(PIN_DIR, HIGH); // back off from switch
      lastStepMicros = micros();
      return false;
    }
  }

  // Step generation (rate limited)
  const uint32_t stepsPerSec = homingBackoff ? BACKOFF_STEPS_PER_SEC : HOME_STEPS_PER_SEC;
  const unsigned long stepIntervalUs = 1000000UL / stepsPerSec;
  unsigned long now = micros();
  if ((unsigned long)(now - lastStepMicros) < stepIntervalUs) return false;
  lastStepMicros = now;
  stepInDirection(homingBackoff ? dirTowardBack() : dirTowardFront());

  if (!homingBackoff) {
    homingStepsTaken++;
    if (homingStepsTaken >= MAX_HOME_STEPS) {
      setFault("HOME_TO");
      return false;
    }
  } else {
    backoffStepsTaken++;
    if (backoffStepsTaken >= BACKOFF_STEPS) {
      homingComplete = true;
      currentPosSteps = 0; // home reference after backoff
      homeValid = true;
      return true;
    }
  }

  return false;
}

void startScan() {
  scanStarted = true;
  scanComplete = false;
  digitalWrite(PIN_ENABLE, LOW);
  scanStartSteps = (long)(START_POS_MM * STEPS_PER_MM + 0.5f);
  scanStopSteps = (long)(STOP_POS_MM * STEPS_PER_MM + 0.5f);
  scanToStart = true;
  scanStepCounter = 0;
  scanStepsTaken = 0;
  scanStepOccurred = false;
  lastStepMicros = micros();
}

bool isScanComplete() {
  scanStepOccurred = false;
  if (scanComplete) return true;

  if (limitBackActive()) {
    setFault("LIM_BACK");
    return false;
  }

  if (scanToStart && currentPosSteps == scanStartSteps) {
    scanToStart = false;
    return false;
  }

  if (!scanToStart) {
    if ((scanStopSteps >= scanStartSteps && currentPosSteps >= scanStopSteps) ||
        (scanStopSteps < scanStartSteps && currentPosSteps <= scanStopSteps)) {
      scanComplete = true;
      return true;
    }
  }

  uint32_t stepsPerSec = scanToStart ? RAPID_STEPS_PER_SEC : SCAN_STEPS_PER_SEC;
  if (!scanToStart && slowScan) {
    stepsPerSec = max<uint32_t>(1, stepsPerSec / 10);
  }
  const unsigned long stepIntervalUs = 1000000UL / stepsPerSec;
  unsigned long now = micros();
  if ((unsigned long)(now - lastStepMicros) < stepIntervalUs) return false;
  lastStepMicros = now;

  if (scanToStart) {
    bool dirHigh = (scanStartSteps > currentPosSteps) ? dirTowardBack() : dirTowardFront();
    stepInDirection(dirHigh);
  } else {
    bool dirHigh = (scanStopSteps > currentPosSteps) ? dirTowardBack() : dirTowardFront();
    stepInDirection(dirHigh);
    scanStepCounter++;
    scanStepOccurred = true;
  }

  scanStepsTaken++;
  if (scanStepsTaken >= MAX_SCAN_STEPS) {
    setFault("SCAN_TO");
    return false;
  }

  return false;
}

void stepPulse() {
  digitalWrite(PIN_STEP, HIGH);
  delayMicroseconds(STEP_PULSE_US);
  digitalWrite(PIN_STEP, LOW);
}

void stepInDirection(bool dirHigh) {
  digitalWrite(PIN_DIR, dirHigh ? HIGH : LOW);
  stepPulse();
  currentPosSteps += dirHigh ? 1 : -1;
}

bool dirTowardFront() {
  return frontDirIsHigh;
}

bool dirTowardBack() {
  return !frontDirIsHigh;
}

bool limitFrontActive() {
  return digitalRead(PIN_LIM_F) == LOW;
}

bool limitBackActive() {
  return digitalRead(PIN_LIM_B) == LOW;
}

