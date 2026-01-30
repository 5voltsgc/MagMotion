/*
 * TDW_SPI.cpp - Library for communicating with TDW main wye boards using the TDW 2 MISO line SPI communication protocol
 * Version 1.0.1
 * 
 * 
 * This library bit-bangs TDW_SPI on the specified pins. This library was written for the Teensy 3.2 microcontroller
 *
 * Version History
 * 1.0.0 - 04/20/17 - Initial Release
 * 1.0.1 - 06/01/17 - Changed resetWye(), getNumberSensors(), and getSensorData() to do error checking and return -1 on errors
 * 1.0.2 - 01/31/2026 - Updated to add timing nobs for SPI transfer bit banging.  
 *
 * Created By: JP Thomas 4/20/17
 */

#define TDW_SPI_VERSION "1.0.2"
#include "Arduino.h"
#include "TDW_SPI.h"

/*
 * TDW_SPI Constructor
 * Initiallizes pins connected to main wye
 */
TDW_SPI::TDW_SPI(int __MOSI, int __MISOA, int __MISOB, int __SCK, int __CS){
  _MOSI = __MOSI;
  _MISOA = __MISOA;
  _MISOB = __MISOB;
  _SCK = __SCK;
  _CS = __CS;
  
  pinMode(_MOSI, OUTPUT);
  pinMode(_MISOA, INPUT);
  pinMode(_MISOB, INPUT);
  pinMode(_SCK, OUTPUT);
  pinMode(_CS, OUTPUT);

  digitalWriteFast(_MOSI, LOW);
  digitalWriteFast(_CS, LOW);
  digitalWriteFast(_SCK, LOW);

  numberSensors = getNumberSensors();
}

/*
 * Sends the wye reset command
 */
int TDW_SPI::resetWye(){
  digitalWriteFast(_CS, HIGH);
  data[0] = spiTransfer(0xBB); //RESET WYE
  data[1] = spiTransfer(0x00);
  digitalWriteFast(_CS, LOW);
  digitalWriteFast(_MOSI, LOW);
  delayMicroseconds(2);
  
  // was   if(data[0]==0xA521 & data[1]==0xABCD){
  if(data[0]==0xA521 && data[1]==0xABCD){
	  return 1;
  }
  else {
	  return int(data[0]);
  }

}

/*
 * Get the number of sensors from the wye
 */
int TDW_SPI::getNumberSensors(){
  resetWye();
  
  digitalWriteFast(_CS, HIGH);
  data[0] = spiTransfer(0xB1); //GET_NUM_SENS
  data[1] = spiTransfer(0x00);
  digitalWriteFast(_CS, LOW);
  digitalWriteFast(_MOSI, LOW);
  
  // was if(data[0]==0xA521 & data[1]<400){
  if(data[0]==0xA521 && data[1]<400){
	  numberSensors = data[1];
	  return data[1];
  }
  else {
	  return -1;
  }
}

/*
 * Get one rotation of sensor data from the wye
 */
int TDW_SPI::getSensorData(uint16_t _sensorData[], int arraySize){
  if(arraySize<numberSensors+2) //if the given array is not large enough to hold all of the sensor data
    return -1; //return error code
    
  digitalWriteFast(_CS, HIGH);
  _sensorData[0] = spiTransfer(0xA0); //AQUIRE
  _sensorData[1] = spiTransfer(0x00); //read response
  for(int i=0; i<numberSensors; i++){
    _sensorData[i+2] = spiTransfer(0x00);
  }
  digitalWriteFast(_CS, LOW);
  digitalWriteFast(_MOSI, LOW);
  
  if(_sensorData[0]==0xA521){
	  return numberSensors;
  }
  else {
	  return -1;
  }
}

/*
 * Internal function that bitbangs the 2 MISO SPI commands
 * NOTE: This version uses explicit timing so CPU speed / compiler optimization won't break it.
 */
uint16_t TDW_SPI::spiTransfer(uint8_t outByte)
{
  uint16_t incoming = 0;

  // --- Timing knobs (start conservative, then tighten) ---
  // Half-cycle delay in nanoseconds. 1000 ns = 1 us.
  // Start at 1000–2000 ns and reduce if you want faster.
  const uint32_t T_SETUP_NS = 500;   // MOSI setup time before clock
  const uint32_t T_HIGH_NS  = 1000;  // clock high duration
  const uint32_t T_LOW_NS   = 1000;  // clock low duration

  // Ensure clock starts low
  digitalWriteFast(_SCK, LOW);

  for (int bit = 0; bit < 8; bit++) {

    // Put next MOSI bit out (MSB first)
    if (outByte & 0x80) digitalWriteFast(_MOSI, HIGH);
    else                digitalWriteFast(_MOSI, LOW);

    delayNanoseconds(T_SETUP_NS);

    // Rising edge
    digitalWriteFast(_SCK, HIGH);
    delayNanoseconds(T_HIGH_NS);

    // Sample while clock is high (typical SPI mode)
    // Pack MISOA into upper byte, MISOB into lower byte
    if (digitalReadFast(_MISOA)) incoming |= (1u << (15 - bit));
    if (digitalReadFast(_MISOB)) incoming |= (1u << (7  - bit));

    // Falling edge
    digitalWriteFast(_SCK, LOW);
    delayNanoseconds(T_LOW_NS);

    outByte <<= 1;
  }

  return incoming;
}

