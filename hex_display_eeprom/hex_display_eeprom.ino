/**
 * This sketch is specifically for programming the EEPROM used in the 8-bit
 * decimal display decoder described in https://youtu.be/dLh1n2dErzE
 */
#define SHIFT_DATA 2
#define SHIFT_CLK 3
#define SHIFT_LATCH 4
#define EEPROM_D0 5
#define EEPROM_D7 12
#define WRITE_EN 13

// Address bits
#define NDISPLAYBITS 3
#define SIGNDISPLAY 4
#define NBITS 12

/* Used with Atmel 256 kbit EEPROM */

/*
   Output the address bits and outputEnable signal using shift registers.
*/
void setAddress(int address, bool outputEnable) {
  shiftOut(SHIFT_DATA, SHIFT_CLK, LSBFIRST, address);
  shiftOut(SHIFT_DATA, SHIFT_CLK, LSBFIRST, (address >> 8) | (outputEnable ? 0x00 : 0x80));

  digitalWrite(SHIFT_LATCH, LOW);
  digitalWrite(SHIFT_LATCH, HIGH);
  digitalWrite(SHIFT_LATCH, LOW);
}


/*
   Read a byte from the EEPROM at the specified address.
*/
byte readEEPROM(int address) {
  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
    pinMode(pin, INPUT);
  }
  setAddress(address, /*outputEnable*/ true);
  delayMicroseconds(1);
  
  byte data = 0;
  for (int pin = EEPROM_D7; pin >= EEPROM_D0; pin -= 1) {
    data = (data << 1) + digitalRead(pin);
  }
  return data;
}


/*
   Write a byte to the EEPROM at the specified address.
*/
void writeEEPROM(int address, byte data) {
  setAddress(address, /*outputEnable*/ false);
  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
    pinMode(pin, OUTPUT);
  }

  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
    digitalWrite(pin, data & 1);
    data = data >> 1;
  }
  digitalWrite(WRITE_EN, LOW);
  delayMicroseconds(1);
  digitalWrite(WRITE_EN, HIGH);
  delay(10);
}


/*
   Read the contents of the EEPROM and print them to the serial monitor.
*/
void printContents() {
  char buf[80];
  int data[16];
  for(int digit = 0; digit < 1; digit++) {
    // Each block contains all 4096 numbers for a specific digit display
    
    for(int sign = 0; sign < 1; sign++) {
      // Each block contains all 2018 numbers for a sign
      Serial.println("\n");
      sprintf(buf, "Digit %d, sign %d\n", digit, sign);
      Serial.println(buf);
      Serial.println("---------------------\n");
      
      for(int val = 0; val<2048; val += 16) {
        // Each block contains all 16 numbers for a line output  
  
        for(int offset = 0; offset <= 15; offset ++) {
          data[offset] = readEEPROM(digit*4096 + sign*2048 + val + offset);
        }
        
        sprintf(buf, "%03x:  %02x %02x %02x %02x %02x %02x %02x %02x   %02x %02x %02x %02x %02x %02x %02x %02x",
                     val, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],
                     data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15]);
        Serial.println(buf);
      }
    }
    Serial.println("\n");
  }
}


int addressToDigitTwosComplement(int address) {
    ;
}


int addressToDigitOnesComplement(int address) {
    int n = (int)pow(2, NBITS);
    int maxn = (int)pow(2, NBITS-1);
    int ndisplay = (int)pow(2, NDISPLAYBITS);
    int sign;
    int magnitude;
    
    int data = address & (n-1);
    if(data & maxn) {
        sign = -1;
        magnitude = n - data - 1;
    }
    else {
        sign = 1;
        magnitude = data;
    }
    int curdisplay = address >> NBITS;

    if(curdisplay == SIGNDISPLAY) {
        if(sign < 0) {
            return 11; // minus
        }
        else {
            return 10; // blank
        }
    }
    if(curdisplay > SIGNDISPLAY) {
      return 10; // blank
    }
    return ((int)(magnitude / pow(10, curdisplay))) % 10;
}


void bla() {
  int digit;
  int naddresses = (int)pow(2, NBITS + NDISPLAYBITS);
  byte digits[] = {
    0x77, // 0
    0x14, // 1
    0xb3, // 2
    0xb6, // 3
    0xd4, // 4
    0xe6, // 5
    0xe7, // 6
    0x34, // 7
    0xf7, // 8
    0xf6, // 9
    0x00, // blank
    0x80  // minus
  };
  
  for(int address = 0; address < naddresses; address ++) {
    digit = addressToDigitOnesComplement(address);
    writeEEPROM(address, digits[digit]);
  }
}


void setup() {
  // put your setup code here, to run once:
  pinMode(SHIFT_DATA, OUTPUT);
  pinMode(SHIFT_CLK, OUTPUT);
  pinMode(SHIFT_LATCH, OUTPUT);
  digitalWrite(WRITE_EN, HIGH);
  pinMode(WRITE_EN, OUTPUT);
  
  // Set up serial communication
  Serial.begin(9600);
  // wait for serial port to connect. Needed for Leonardo only
  while (!Serial) {
    ;
  }

  bla();
  
  // Read and print out the contents of the EERPROM
  Serial.println("\n\nReading EEPROM");
  printContents();
    
}

void loop() {
  // put your main code here, to run repeatedly:

}
