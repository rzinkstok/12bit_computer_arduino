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
}

void resetControls() {
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
  resetControls();
  digitalWrite(BANK_IN, LOW);
  dataOut(bank);
  pulsePin(CLOCK_OUT, HIGH);
}

void setAddress(int address) {
  resetControls();
  digitalWrite(ADDRESS_IN, LOW);
  delay(PULSE_DELAY);
  dataOut(address);
  delay(PULSE_DELAY);
  stepClock();
}

void writeData(int data) {
  resetControls();
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
  Serial.begin(9600);
  // wait for serial port to connect. Needed for Leonardo only
  while (!Serial) {
    ;
  }

  Serial.println("Reset");
  resetControls();

  for(int i = 0; i<128; i++) {
    writeMemory(1, i, i*i);  
  }
  Serial.println("DONE!");
 
}

void loop() {
  // put your main code here, to run repeatedly:

}
