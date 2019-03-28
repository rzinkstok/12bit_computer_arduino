#define NDATAPINS 8
#define NADDRESSPINS 17
#define PAGESIZE 128
#define NPAGES 8192
#define ARRAY_SIZE 16384
#define NDATA_ARRAYS 8

// Signals
#define HLT 0b00000000000000000000000000000001 // Halt clock
#define BAI 0b00000000000000000000000000000010 // Bank address in
#define MAI 0b00000000000000000000000000000100 // Memory address in
#define RDI 0b00000000000000000000000000001000 // RAM data in
#define RDO 0b00000000000000000000000000010000 // RAM data out
#define IRI 0b00000000000000000000000000100000 // Instruction register in
#define IRO 0b00000000000000000000000001000000 // Instruction register out
#define ARI 0b00000000000000000000000010000000 // A register in

#define ARO 0b00000000000000000000000100000000 // A register out
#define BRI 0b00000000000000000000001000000000 // B register in
#define BRO 0b00000000000000000000010000000000 // B register out
#define SRO 0b00000000000000000000100000000000 // Sum register out
#define SUB 0b00000000000000000001000000000000 // ALU subtract
#define ORI 0b00000000000000000010000000000000 // Output register in
#define PCE 0b00000000000000000100000000000000 // Program counter enable
#define PCO 0b00000000000000001000000000000000 // Program counter out

#define JMP 0b00000000000000010000000000000000 // Jump (program counter in)
#define FRI 0b00000000000000100000000000000000 // Flags register in
#define EXT 0b00000000000001000000000000000000 // Extend
#define CEX 0b00000000000010000000000000000000 // Clear extend


struct pin_t {
    volatile uint8_t *r;
    uint8_t b;
};

int writeEnablePinNumber = 22;
pin_t writeEnable;

int outputEnablePinNumber = 36;
pin_t outputEnable;

int dataPinNumbers[] = {49, 51, 53, 50, 48, 46, 44, 42};
pin_t dataPins[NDATAPINS];

int addressPinNumbers[] = {12, 11, 10, 9, 8, 7, 6, 5, 30, 32, 38, 34, 4, 28, 26, 3, 2};
pin_t addressPins[NADDRESSPINS];


void initPins() {
    int pinNumber;

    writeEnable.r = portOutputRegister(digitalPinToPort(writeEnablePinNumber));
    writeEnable.b = digitalPinToBitMask(writeEnablePinNumber);
    pinMode(writeEnablePinNumber, OUTPUT);
    digitalWrite(writeEnablePinNumber, HIGH);

    outputEnable.r = portOutputRegister(digitalPinToPort(outputEnablePinNumber));
    outputEnable.b = digitalPinToBitMask(outputEnablePinNumber);
    pinMode(outputEnablePinNumber, OUTPUT);
    digitalWrite(outputEnablePinNumber, HIGH);

    for (int i = 0; i < NDATAPINS; i++) {
        pinNumber = dataPinNumbers[i];
        dataPins[i].r = portOutputRegister(digitalPinToPort(pinNumber));
        dataPins[i].b = digitalPinToBitMask(pinNumber);
        pinMode(pinNumber, OUTPUT);
        digitalWrite(pinNumber, LOW);
    }

    for (int i = 0; i < NADDRESSPINS; i++) {
        pinNumber = addressPinNumbers[i];
        addressPins[i].r = portOutputRegister(digitalPinToPort(pinNumber));
        addressPins[i].b = digitalPinToBitMask(pinNumber);
        pinMode(pinNumber, OUTPUT);
        digitalWrite(pinNumber, LOW);
    }
}


void pinLow(pin_t pin) {
    *pin.r &= ~pin.b;
}


void pinHigh(pin_t pin) {
    *pin.r |= pin.b;
}


void writePin(pin_t pin, uint8_t val) {
    if (val == LOW) {
        *pin.r &= ~pin.b;
    }
    else {
        *pin.r |= pin.b;
    }
}


void setPinsToDefaultForReading() {
    for (int p = 0; p < NDATAPINS; p++) {
        pinMode(dataPinNumbers[p], INPUT);
    }
    for (int p = 0; p < NADDRESSPINS; p++) {
        pinMode(addressPinNumbers[p], OUTPUT);
    }

    pinMode(outputEnablePinNumber, OUTPUT);
    digitalWrite(outputEnablePinNumber, LOW); // always read
    pinMode(writeEnablePinNumber, OUTPUT);
    digitalWrite(writeEnablePinNumber, HIGH);

    delay(10);
}


void setPinsToDefaultForWriting() {
    for (int p = 0; p < NDATAPINS; p++) {
        pinMode(dataPinNumbers[p], OUTPUT);
        digitalWrite(dataPinNumbers[p], LOW);
    }
    for (int p = 0; p < NADDRESSPINS; p++) {
        pinMode(addressPinNumbers[p], OUTPUT);
    }

    pinMode(outputEnablePinNumber, OUTPUT);
    digitalWrite(outputEnablePinNumber, HIGH);
    pinMode(writeEnablePinNumber, OUTPUT);
    digitalWrite(writeEnablePinNumber, HIGH);

    delay(10);
}


void outputAddress(unsigned long address) {
    for (int p = 0; p < NADDRESSPINS; p++) {
        writePin(addressPins[p], address & 1);
        address = address >> 1;
    }
}


byte readEEPROM(unsigned long address) {
    outputAddress(address);

    // Perform the read
    byte data = 0;
    for (int p = 0; p < NDATAPINS; p++) {
        data = data + (digitalRead(dataPinNumbers[p]) << p);
    }
    return data;
}


void writeEEPROM(unsigned long address, byte data) {
    // End the previous write if there was one
    writePin(writeEnable, HIGH);

    // Show the new address to the EEPROM
    outputAddress(address);

    // Set up the data
    for (int p = 0; p < NDATAPINS; p++) {
        writePin(dataPins[p], data & 1);
        data = data >> 1;
    }

    // Start the write
    writePin(writeEnable, LOW);
}

void startPageWrite(int page) {
    for (int i = 0; i < 16; i++)  { // the first 2-16 bytes written in each page are skipped for some reason, so write 16 useless bytes
        writeEEPROM(page * PAGESIZE, 0xff);
    }
}


void endPageWrite() {
    writePin(writeEnable, HIGH);
    delay(20);
}



void printPage(int page) {
    char buf[80];
    byte data[16];
    unsigned long start = page * PAGESIZE;

    sprintf(buf, "\nPage %d", page);
    Serial.println(buf);
    Serial.flush();

    for (int base = 0; base < PAGESIZE; base += 16) // for every 16 addresses in the EEPROM
    {
        for (int offset = 0; offset < 16; offset++) // for each address within the current set of 16 addresses
        {
        data[offset] = readEEPROM(start + base + offset);
        }

        sprintf(buf, "%05lx: %02x %02x %02x %02x %02x %02x %02x %02x   %02x %02x %02x %02x %02x %02x %02x %02x",
                start + base, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10],
                data[11], data[12], data[13], data[14], data[15]);
        // the %05lx above has an L, not a one

        Serial.println(buf);
        Serial.flush();
    }
}


byte get_ucode_byte(int instruction, int step, int flags, int byte_sel) {
    unsigned long ucode = 0;

    switch(step) {
        case 0:
            ucode = MAI | PCO;
            break;
        case 1:
            ucode = RDO | IRI | PCE;
            break;
        case 2:
            if(
                (instruction == 5) | 
                (instruction == 6) | 
                (instruction == 8) | 
                (instruction == 12) | 
                (instruction == 13)
            ) {
                ucode = IRO | MAI;
                break;
            }
        
            if(instruction == 0) {
                ucode = IRO | JMP;
            }
            if(instruction == 11) {
                ucode = ARO | ORI;
            }
            if(instruction == 14) {
                ucode = EXT;
            }
            if(instruction == 15) {
                ucode = HLT;
            }
            break;
        case 3:
            if(instruction == 5) {
                ucode = RDO | ARI;
            }
            if(instruction == 6) {
                ucode = ARO | RDI;
            }
            if(instruction == 8) {
                ucode = RDO | BRI;
            }
            if(instruction == 12) {
                ucode = RDO | ORI;
            }
            if(instruction == 13) {
                ucode = RDO | BRI;
            }
            break;
        case 4:
            if(instruction == 8) {
                ucode = SRO | ARI | FRI;
            }
            if(instruction == 13) {
                ucode = SUB | SRO | ARI | FRI;
            }
            break;
        case 5:
            break;
        case 6:
            break;
        case 7:
            break;
        case 8:
            break;
        case 9:
            break;
        case 10:
            break;
        case 11:
            if(instruction >=16) {
                ucode = CEX;
            }
            break;
        default:
            break;
    }

    return (ucode >> (byte_sel * 8)) & 255;
}


void setup() {
    // put your setup code here, to run once:
    char buf[80];
    uint32_t nbytes = (unsigned long)pow(2, 17);
    uint32_t startAddress = 0;
    uint32_t maxAddress = startAddress + nbytes;
    
    int instruction;
    int step;
    int byte_sel;
    int flags1, flags2, flags;
    int unused;
    byte d;
    
    Serial.begin(115200);
    while (!Serial) {
        delay(10);
    }
    
    initPins();
    setPinsToDefaultForWriting();
    Serial.println("Programming EEPROM");
    Serial.flush();

    for (uint32_t address = startAddress; address < maxAddress; address++) {
        if ((address % PAGESIZE) == 0) {
            if (address > 0) {
                endPageWrite();
            }
            startPageWrite(address / PAGESIZE);
            if ((address % (16 * PAGESIZE)) == 0) {
                Serial.print(".");
            }
        }

        instruction = (address & 0b00000000000011111);
        step =        (address & 0b00000000111100000) >> 5;
        byte_sel =    (address & 0b00000011000000000) >> 9;
        unused =      (address & 0b00000100000000000) >> 11;
        flags1 =      (address & 0b00001000000000000) >> 12;  // Just correct for the unused bit on the right
        unused =      (address & 0b00010000000000000) >> 13;
        flags2 =      (address & 0b11100000000000000) >> 13;
        flags = flags1 + flags2;

        d = get_ucode_byte(instruction, step, flags, byte_sel);
        writeEEPROM(address, d);
    }
    endPageWrite();

    Serial.println("done!");
    Serial.flush();

    setPinsToDefaultForReading();
    for (int i = 0; i < 4; i++) {
        printPage(i);
    }
    Serial.println("\nDone reading");
    Serial.flush();
}

void loop() {
    // put your main code here, to run repeatedly:
}
