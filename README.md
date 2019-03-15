# Arduino source code for a 12-bit computer

This project is part of my attempt to extend the 8-bit computer as demonstrated by Ben Eater (see https://eater.net/8bit) to 12-bit.

To be able to use more memory and instructions, I'm using a different RAM 
chip (32k x 8, Lyontek LY62256PL) and four 1 Mbit EEPROMs (Greenliant 
GLS29EE010) for the control logic. The hex display is extended to 4 digits 
and 1 sign, so it needs a 32k x 8 bit EEPROM (Atmel AT28C256). 

To facilitate the process of programming these, I used an Arduino Micro for the
RAM, and an Arduino Mega for the EEPROMS (as the Micro has insufficient memory
for loading the data into the 1 Mbit EEPROMS).

This repo contains all the source code for this.
