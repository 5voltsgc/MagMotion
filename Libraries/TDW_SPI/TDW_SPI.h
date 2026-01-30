/*
 * TDW_SPI.h - Library for communicating with TDW main wye boards using the TDW 2 MISO line SPI communication protocol
 * Version 1.0.1
 * 
 * 
 * This library bit-bangs TDW_SPI on the specified pins. This library was written for the Teensy 3.2 microcontroller
 *
 * Version History
 * 1.0.0 - 04/20/17 - Initial Release
 * 1.0.1 - 06/01/17 - Changed resetWye(), getNumberSensors(), and getSensorData() to do error checking and return -1 on errors
 *
 * Created By: JP Thomas 4/20/17
 */
#ifndef TDW_SPI_h
#define TDW_SPI_h

#include "Arduino.h"


class TDW_SPI{
  public:
    TDW_SPI(int __MOSI, int __MISOA, int __MISOB, int __SCK, int __CS);
    int resetWye();
    int getNumberSensors();
    int getSensorData(uint16_t _sensorData[], int arraySize);
    
  private:
    uint16_t spiTransfer(uint8_t _data);
    
    static const int buffer_size = 64;
    uint16_t data[buffer_size];
    uint8_t numberSensors;
    int _MOSI;
    int _MISOA;
    int _MISOB;
    int _SCK;
    int _CS;
};

#endif
