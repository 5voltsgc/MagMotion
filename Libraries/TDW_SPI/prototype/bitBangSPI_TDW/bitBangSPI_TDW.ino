#define _MISOA 2
#define _MISOB 1
#define _MOSI 3
#define _CS 0
#define _SCK 4

const int buffer_size = 64;
uint16_t data[buffer_size];
uint8_t numberSensors = 0;

//Assuming TDW SPI is using MODE 0
//Assuming data is MSB first
//CS is active HIGH

//bitbang spi
uint16_t SpiTransfer(uint8_t _data)
{
  uint16_t incoming_data = 0;
  for (int i=0; i<8; i++) {
    if (_data & 0x80) //set/clear mosi bit
    digitalWriteFast(_MOSI, HIGH);
    else
    digitalWriteFast(_MOSI, LOW);
  
    _data <<= 1; //shift for next bit
    
    if (digitalRead(_MISOA)) //capture miso bits
    incoming_data |= 1<<(15-i);  //high byte

    if (digitalRead(_MISOB))
    incoming_data |= 1<<(7-i);  //low byte
    
    digitalWriteFast(_SCK, HIGH);
    digitalWrite(_SCK, LOW);
    
    //PORTD |= (1<<PORTD7); //pulse clock
    //asm volatile ("nop \n\t"); //pause
    //PORTD &= ~(1<<PORTD7);
  }
  return incoming_data;
}

void printBuffer(bool decimal)
{
  for(int i=0; i<buffer_size; i++)
  {
    if(decimal)
    Serial.print(data[i], DEC);
    else
    Serial.print(data[i], HEX);
    
    Serial.print(" ,  ");
  }
  Serial.println();
}

void resetWye()
{
  digitalWriteFast(_CS, HIGH);
  data[0] = SpiTransfer(0xBB); //RESET WYE
  data[1] = SpiTransfer(0x00);
  digitalWriteFast(_CS, LOW);
  delayMicroseconds(2);
}

uint8_t getNumSens()
{
  resetWye();
  
  digitalWriteFast(_CS, HIGH);
  data[0] = SpiTransfer(0xB1); //GET_NUM_SENS
  data[1] = SpiTransfer(0x00);
  digitalWriteFast(_CS, LOW);
  
  return data[1];
}

void getSensData(uint8_t numSens)
{
  digitalWriteFast(_CS, HIGH);
  data[0] = SpiTransfer(0xA0);
  data[1] = SpiTransfer(0x00);
  for(int i=0; i<numSens; i++)
  {
    if(i+2 >=  64)
    break;
    
    data[i+2] = SpiTransfer(0x00);
  }
  digitalWriteFast(_CS, LOW);
}


void setup(void)
{
  Serial.begin(115200);
  while(!Serial); //wait for connection to serial port
  //configure pins
  pinMode(_MISOA, INPUT);
  pinMode(_MISOB, INPUT);
  pinMode(_MOSI, OUTPUT);
  pinMode(_CS, OUTPUT);
  pinMode(_SCK, OUTPUT);
  
  digitalWriteFast(_CS, LOW);
  digitalWriteFast(_SCK, LOW);
  
  numberSensors = getNumSens();
  Serial.print("Number of Sensors: ");
  Serial.println(numberSensors);
}

void loop()
{
  long startTime = micros();
  getSensData(numberSensors);
  printBuffer(true);
  //Serial.flush();
  long endTime = micros();
  //Serial.print("\n\nIt took ");
  //Serial.print(endTime - startTime);
  //Serial.println(" microseconds to read a rotation");
  
  //data = SpiTransfer(0xA0); //ACQUIRE
  //data = SpiTransfer(0xA2); //SEND_SPOOFED_SENSOR_DATA
  //data = SpiTransfer(0xB1); //GET_NUMBER_OF_SENSORS
  //data = SpiTransfer(0xBB); //RESET_Y

  Serial.println();
  delay(500);
  
}


