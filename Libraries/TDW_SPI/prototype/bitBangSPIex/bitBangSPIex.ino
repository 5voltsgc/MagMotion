 //FM24CL64B SPI F-RAM
 //64-Kbit
 //
 //bit-bang
 //
 /*
 Arduino--Logic Conv--FRAM
 D7-------TXH/TXL-----6.SCK
 D6-------------------2.MISO
 D5-------TXH/TXL-----5.MOSI
 D4-------------------1.CS
 3V3------LV
 5V-------HV
 GND------HV GND
 GND------------------4.VSS
 3V3------------------8.VCC
 3V3------------------7.HOLD (tie to Vcc if not used)
 3V3------[10KR]------1.CS
 3.WP (active low, tie to Vcc if not used)
 */

 //bitbang
 uint8_t SpiTransfer(uint8_t _data) {
 for (uint8_t bit=0; bit<8; bit++) {
 if (_data & 0x80) //set/clear mosi bit
 PORTD |= (1<<PORTD5);
 else
 PORTD &= ~(1<<PORTD5);
 _data <<= 1; //shift for next bit
 if (PIND) //capture miso bit
 _data |= (PIND & (1<<PORTD6)) != 0;
 PORTD |= (1<<PORTD7); //pulse clock
 asm volatile ("nop \n\t"); //pause
 PORTD &= ~(1<<PORTD7);
 }
 return _data;
 }

//SRAM opcodes
 #define WREN 0b00000110 //set write enable latch
 #define WRDI 0b00000100 //write disable
 #define RDSR 0b00000101 //read status register
 #define WRSR 0b00000001 //write status register
 #define READ 0b00000011 //read memory data
 #define WRITE 0b00000010 //write memory data

uint8_t SpiRAMRead8(uint16_t address) {
 uint8_t read_byte;

PORTD &= ~(1<>8)&0xff));
 SpiTransfer((char)address);
 read_byte = SpiTransfer(0xff);
 PORTD |= (1<<PORTD4); //set CS high
 return read_byte;
 }

void SpiRAMWrite8(uint16_t address, uint8_t data) {
 PORTD &= ~(1<<PORTD4); //set CS low
 SpiTransfer(WREN);
 PORTD |= (1<<PORTD4); //set CS high
 PORTD &= ~(1<>8)&0xff));
 SpiTransfer((char)address);
 SpiTransfer(data);
 PORTD |= (1<<PORTD4); //set CS high
 }

void setup(void) {
 uint16_t addr;
 uint8_t i, sreg;

Serial.begin(9600);
 //configure pins
 pinMode(4, OUTPUT); //CS
 pinMode(5, OUTPUT); //MOSI
 pinMode(6, INPUT); //MISO
 pinMode(7, OUTPUT); //SCK
 PORTD |= (1<<PORTD4); //set CS high
 PORTD &= ~_BV(PORTD7); //set clock low

//test it
 for (addr=0; addr<32; addr++) {
 SpiRAMWrite8(addr, (uint8_t)addr);
 Serial.print("Addr: ");
 Serial.print(addr);
 i = SpiRAMRead8(addr);
 Serial.print(" | Read: ");
 Serial.println((uint16_t)i);
 }
 }

void loop() { }


