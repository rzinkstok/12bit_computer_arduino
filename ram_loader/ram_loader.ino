// Shifter pins
#define SHIFT_DATA 8  // SER input, pin 14
#define SHIFT_CLOCK 10 // SRCLK input, pin 11
#define SHIFT_LATCH 9 // RCLK input, pin 12

// Control signals
#define CLOCK_OUT 7
#define BANK_IN 12
#define ADDRESS_IN 11
#define MEM_IN 13

// Delays
#define PULSE_WIDTH 1 // ms
#define PULSE_DELAY 1 // ms

void pulsePin(int pin, bool level) {
    // Take the given pin to the given level and back
    delay(PULSE_DELAY);
    digitalWrite(pin, !level);
    delay(PULSE_DELAY);
    digitalWrite(pin, level);
    delay(PULSE_WIDTH);
    digitalWrite(pin, !level);
    delay(PULSE_DELAY);
}

void stepClock() {
    pulsePin(CLOCK_OUT, HIGH);
    delay(500);
}

void setControlsForWriting() {
    digitalWrite(CLOCK_OUT, LOW);
    digitalWrite(ADDRESS_IN, HIGH);
    digitalWrite(BANK_IN, HIGH);
    digitalWrite(MEM_IN, HIGH);
    delay(PULSE_DELAY);
}

void dataOut(int data) {
    shiftOut(SHIFT_DATA, SHIFT_CLOCK, LSBFIRST, data);
    shiftOut(SHIFT_DATA, SHIFT_CLOCK, LSBFIRST, (data >> 8));
    pulsePin(SHIFT_LATCH, HIGH);
}

void setBank(int bank) {
    setControlsForWriting();
    digitalWrite(BANK_IN, LOW);
    dataOut(bank);
    pulsePin(CLOCK_OUT, HIGH);
}

void setAddress(int address) {
    setControlsForWriting();
    digitalWrite(ADDRESS_IN, LOW);
    delay(PULSE_DELAY);
    dataOut(address);
    delay(PULSE_DELAY);
    stepClock();
}

void writeData(int data) {
    setControlsForWriting();
    digitalWrite(MEM_IN, LOW);
    dataOut(data);
    stepClock();
}

void writeMemory(int bank, int address, int data) {
    if(address>127) {
        exit(1);
    }
    if(bank<0) {
        setAddress(address);
    }
    else {
        setBank(bank);
        setAddress(address + 128);
    }
    writeData(data);
}

void setup() {
    // put your setup code here, to run once:
    pinMode(SHIFT_DATA, OUTPUT);
    pinMode(SHIFT_CLOCK, OUTPUT);
    pinMode(SHIFT_LATCH, OUTPUT);
    pinMode(CLOCK_OUT, OUTPUT);
    pinMode(ADDRESS_IN, OUTPUT);
    pinMode(BANK_IN, OUTPUT);
    pinMode(MEM_IN, OUTPUT);
    
    // Set up serial communication
    Serial.begin(115200);
    // wait for serial port to connect. Needed for Leonardo only
    while (!Serial) {
        ;
    }

    char buf[80];
    Serial.println("Reset");
    setControlsForWriting();

    if(0) {
        // Load into A: opcode 5, address 16
        writeMemory(-1, 0, (5 << 8) + 16);
        // Add to B: opcode 8, address 17
        writeMemory(-1, 1, (8 << 8) + 17);
        // Subtract from B: opcode 13, address 17
        //writeMemory(-1, 1, (13 << 8) + 17);
        // Output A: opcode 11, address n/a
        writeMemory(-1, 2, (11 << 8));
        // Halt: opcode 15, address n/a
        writeMemory(-1, 3, (15 << 8));
        // 325 in address 16
        writeMemory(-1, 16, 7);
        // 86 in address 17
        writeMemory(-1, 17, 2);

        // for(int i=0; i<13; i++) {
        //     setAddress(i);
        //     delay(1000);
        // }
        // delay(100000);
    }
    if(1) {
        // Load into A: opcode 5, address 16
        writeMemory(-1, 0, (5 << 8) + 16);
        // Output A: opcode 11, address n/a
        writeMemory(-1, 1, (11 << 8));
        // Branch on zero: opcode 9, address 5
        writeMemory(-1, 2, (9 << 8) + 5);
        // Subtract 1: opcode 13, address 17
        writeMemory(-1, 3, (13 << 8) + 17);
        // Jump: opcode 0, address 1
        writeMemory(-1, 4, (0 << 8) + 1);
        // Halt: opcode 15, address n/a
        writeMemory(-1, 5, (15 << 8));

        // 5 in addres 16
        writeMemory(-1, 16, 5);
        // 1 in address 17
        writeMemory(-1, 17, 1);
    }
    Serial.println("DONE!");
    
  
}

void loop() {
    // put your main code here, to run repeatedly:

}
