/*
 * ReadSensorData.ini - Example of reading rotations from a main wye
 * 
 * Created By: JP Thomas   4/20/17
 */
#include "TDW_SPI.h"

//define the pins the main wye is connected to
#define _MISOA 2
#define _MISOB 1
#define _MOSI 3
#define _CS 0
#define _SCK 4

//create a buffer to store a full rotation
const int buffer_size = 26;
uint16_t data[buffer_size];
uint8_t numberSensors = 0;

//instantiate the spi class (enables data reading from main wye)
TDW_SPI spi = TDW_SPI(_MOSI, _MISOA, _MISOB, _SCK, _CS);

//function to print the rotation data in a readable format
void printBuffer(bool decimal){
  for(int i=0; i<buffer_size; i++){
    if(decimal)
    Serial.print(data[i], DEC);
    else
    Serial.print(data[i], HEX);
    
    Serial.print(" ,  ");
  }
  Serial.println();
}

void setup(void){
  Serial.begin(115200);
  while(!Serial); //wait for connection to serial port

  //get the number of sensors connected to the main wye (number of sensors in one rotation)
  Serial.print("Number of Sensors: ");
  Serial.println(spi.getNumberSensors());
}

void loop(){

  //get rotation from main wye
  int response = spi.getSensorData(data, buffer_size); //data is stored in the "data" buffer
  
  //check for errors
  if(response == -1){
    Serial.println("\n\nERROR!");
    Serial.print("Data buffer is not long enough\nData buffer is only ");
    Serial.print(sizeof(data)/2);
    Serial.print(" long but needs to be at least ");
    Serial.println(spi.getNumberSensors()+2);
  }
  else{
    printBuffer(false);
    Serial.println();
  }
  
  delay(5000);
}


