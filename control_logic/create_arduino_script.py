import jinja2
from copy import deepcopy


# Signals
HLT = int('0b00000000000000000000000000000001', 2)  # Halt clock
BAI = int('0b00000000000000000000000000000010', 2)  # Bank address in
MAI = int('0b00000000000000000000000000000100', 2)  # Memory address in
RDI = int('0b00000000000000000000000000001000', 2)  # RAM data in
RDO = int('0b00000000000000000000000000010000', 2)  # RAM data out
IRI = int('0b00000000000000000000000000100000', 2)  # Instruction register in
IRO = int('0b00000000000000000000000001000000', 2)  # Instruction register out
ARI = int('0b00000000000000000000000010000000', 2)  # A register in

ARO = int('0b00000000000000000000000100000000', 2)  # A register out
BRI = int('0b00000000000000000000001000000000', 2)  # B register in
BRO = int('0b00000000000000000000010000000000', 2)  # B register out
SRO = int('0b00000000000000000000100000000000', 2)  # Sum register out
SUB = int('0b00000000000000000001000000000000', 2)  # ALU subtract
ORI = int('0b00000000000000000010000000000000', 2)  # Output register in
PCE = int('0b00000000000000000100000000000000', 2)  # Program counter enable
PCO = int('0b00000000000000001000000000000000', 2)  # Program counter out

JMP = int('0b00000000000000010000000000000000', 2)  # Jump (program counter in)
FRI = int('0b00000000000000100000000000000000', 2)  # Flags register in
EXT = int('0b00000000000001000000000000000000', 2)  # Extend
CEX = int('0b00000000000010000000000000000000', 2)  # Clear extend


# AGC instructions:
"""
TC     - Transfer control
TCF    - Transfer control to fixed memory
CCS    - Count, compare, and skip
BZF    - Branch on zero to fixed memory
BZMF   - Branch on zero or minus to fixed memory
CA     - Clear and add
CS     - Clear and subtract
DCA    - Double precision clear and add
DCS    - Double precision clear and subtract
TS     - Transfer to storage
XCH    - Exchange A
QXCH   - Exchange Q
LXCH   - Exchange L
DXCH   - Double exchange
NDX    - Index basic / extracode (2 instructions)
AD     - Add
SU     - Subtract
MP     - Multiply
DV     - Divide
ADS    - Add and store
DAS    - Double precision add and store
INCR   - Increment
AUG    - Augment
DIM    - Diminish
MSU    - Modular subtract (angular subtraction)
MSK    - Mask or AND
READ   - Read channel
RAND   - Read and AND
ROR    - Read and OR
RXOR   - Read and EXCLUSIVE OR
WRITE  - Write channel
WAND   - Write and AND
WOR    - Write and OR
RELINT - Release interrupt inhibit
INHINT - Inhibit interrupt
EXTEND - Extend order code field
RESUME - Resume interrupted program
CYR    - Cycle right
SR     - Shift right
CYL    - Cycle left
EDOP   - Edit operator
RUPT   - Interrupt
GOJ    - Start
PINC   - Plus increment
MINC   - Minus increment or decrement
DINC   - Diminish increment
PCDU   - Increment CDU
MCDU   - Decrement CDU
SHINC  - Shift increment
SHANC  - Shift add increment
TCSAJ  - Transfer control to specified address
FETCH  - Read memory
INOTRD - Read channel
STORE  - Load memory
INOTLD - Load channel

55 instructions
Excluding channel, double, CDU, interrupt, counter, fixed memory, and peripheral instructions:


Implement right away:
TC     - 00 - Transfer control: take next instruction from K; stores I+1 in Q
GOJ    - 00 - Start
CCS    - 01 - Count, compare, and skip: four way (-, -0, +0, +) comparison of c(E)
INCR   - 02.4 - Increment: adds +1 to E
ADS    - 02.6 - Add and store: adds c(A) to c(E) and store in A and E
CA     - 03 - Clear and add: copies c(K) into A
CS     - 04 - Clear and subtract: copies complement of c(K) into A
TS     - 05.4 - Transfer to storage: if c(A) is not an overflow quantity, copies c(A) into K; if c(A) is positive overflow, copies c(A) into K, sets c(A) to +1; if c(A) is negative overflow, copies c(A) into K, sets c(A) to -1
XCH    - 05.6 - Exchange A: exchanges c(A) with c(E)
NDX    - 05.0 - Index basic / extracode 15 (2 instructions): adds c(K) to c(I+1) where I is location of NDX E; takes sum of c(K) + c(I+1) as next instruction
AD     - 06 - Add: add c(K) to A
BZF    - 11 - Branch on zero to fixed memory: next instruction from F if A is +0
BZMF   - 16.2,4,6 - Branch on zero or minus to fixed memory: next instruction from F if A is +0 or negative
AUG    - 12.4 - Augment: adds +1 to abs(E)
DIM    - 12.6 - Diminish: adds -1 to abs(E)
SU     - 16.0 - Subtract: subtracts c(A) from c(E); stores result in A
EXTEND - Extend order code field

Instructions not present in AGC:
HLT    - Halt the clock
AOUT   - Display c(A)
OUT    - Display c(E) 
JZ     - Jump on zero, perhaps not needed
JC     - Jump on carry, perhaps not needed
LDI    - Load address in instruction register into A
LDA    - Equal to CA
ADD    - Equal to AD
SUB    - Equal to SU
STA    - Equal to TS
JMP    - Equal to TC

First complete list:

0 0000 TC
0 0001 GOJ
0 0010 CCS
0 0011 INCR
0 0100 ADS
0 0101 CA
0 0110 TS
0 0111 XCH
0 1000 AD
0 1001 BZF
0 1010 BZMF
0 1011 AOUT
0 1100 OUT
0 1101 SU
0 1110 EXTEND
0 1111 HLT

1 0000 CS
1 0001 NDX
1 0010 AUG
1 0011 DIM



Needs additional hardware:

Q register:
QXCH   - Exchange Q: exchanges c(Q) with c(E)

L register:
LXCH   - Exchange L: exchanges c(L) with c(E)
MP     - Multiply: multiplies c(A) by c(E); stores result in A and L
DV     - Divide: divides c(A, L) by c(E); stores quotient in A and remainder in L

Extend flip-flop:


AND register:
MSK    - Mask or AND: AND's c(A) with c(K); stores result in A

Do not implement for now
MSU    - Modular subtract (angular subtraction): forms the signed one's complement difference between c(A) and c(E) where c(A) and c(E) are unsigned two's complement numbers; stores result in A

CYR    - Cycle right: cycles quantity in 0020 one place to the right
SR     - Shift right: shifts quantity in 0021 one place to the right
CYL    - Cycle left: cycles quantity in 0022 one place to the left
EDOP   - Edit operator: shifts quantity in 0023 seven places to the left



Complications:
Testing control pulses act on values asserted on the write lines, or on the contents of A or G:
TMZ   - Test for minus zero    - WL1-16 - sets BR2 if -000000
TOV   - Test for overflow      - A      - sets BR1 and BR2 to 00 if no overflow, 01 for + overflow, 10 for - overflow 
TPZG  - Test for positive zero - G      - sets BR2 if +000000
TSGN  - Test for sign          - WL16   - sets BR1 if negative
TSGN2 - Test for sign          - WL16,  - sets BR2 if negative
TSGU  - Test sign of U         - U      - sets BR1 if negative

"""


# Instruction template
UCODE_TEMPLATE = [
# Step:
#    0              1                   2           3           4                       5   6   7   8   9   10  11      12  13  14  15
    [MAI | PCO,     RDO | IRI | PCE,    IRO | JMP,  0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 0000 - TC
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 0001 - GOJ
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 0010 - CCS
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 0011 - INCR
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 0100 - ADS
    [MAI | PCO,     RDO | IRI | PCE,    IRO | MAI,  RDO | ARI,  0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 0101 - CA
    [MAI | PCO,     RDO | IRI | PCE,    IRO | MAI,  ARO | RDI,  0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 0110 - TS
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 0111 - XCH
    [MAI | PCO,     RDO | IRI | PCE,    IRO | MAI,  RDO | BRI,  SRO | ARI | FRI,        0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 1000 - AD
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 1001 - BZF
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 1010 - BFZM
    [MAI | PCO,     RDO | IRI | PCE,    ARO | ORI,  0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 1011 - AOUT
    [MAI | PCO,     RDO | IRI | PCE,    IRO | MAI,  RDO | ORI,  0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 1100 - OUT
    [MAI | PCO,     RDO | IRI | PCE,    IRO | MAI,  RDO | BRI,  SUB | SRO | ARI | FRI,  0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 1101 - SU
    [MAI | PCO,     RDO | IRI | PCE,    EXT,        0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 1110 - EXTEND
    [MAI | PCO,     RDO | IRI | PCE,    HLT,        0,          0,                      0,  0,  0,  0,  0,  0,  0,      0,  0,  0,  0],  # 0 1111 - HLT
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 0000 - CS
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 0001 - NDX
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 0010 - AUG
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 0011 - DIM
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 0100 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 0101 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 0110 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 0111 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 1000 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 1001 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 1010 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 1011 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 1100 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 1101 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 1110 -
    [MAI | PCO,     RDO | IRI | PCE,    0,          0,          0,                      0,  0,  0,  0,  0,  0,  CEX,    0,  0,  0,  0],  # 1 1111 -
]


# print((UCODE_TEMPLATE[0][4] >> 3*8) & 255)
# import sys
# sys.exit()

# Instructions per flag combination
# Flags:
# - Positive overflow
# - Nagative overflow
# - Zero
# - Negative

# Flags  0: positive overflow 0, negative overflow 0, zero 0, negative 0
f00 = deepcopy(UCODE_TEMPLATE)
# Flags  1: positive overflow 1, negative overflow 0, zero 0, negative 0
f01 = deepcopy(UCODE_TEMPLATE)
# Flags  2: positive overflow 0, negative overflow 1, zero 0, negative 0
f02 = deepcopy(UCODE_TEMPLATE)
# Flags  3: positive overflow 1, negative overflow 1, zero 0, negative 0
f03 = deepcopy(UCODE_TEMPLATE)
# Flags  4: positive overflow 0, negative overflow 0, zero 1, negative 0
f04 = deepcopy(UCODE_TEMPLATE)
# Flags  5: positive overflow 1, negative overflow 0, zero 1, negative 0
f05 = deepcopy(UCODE_TEMPLATE)
# Flags  6: positive overflow 0, negative overflow 1, zero 1, negative 0
f06 = deepcopy(UCODE_TEMPLATE)
# Flags  7: positive overflow 1, negative overflow 1, zero 1, negative 0
f07 = deepcopy(UCODE_TEMPLATE)
# Flags  8: positive overflow 0, negative overflow 0, zero 0, negative 1
f08 = deepcopy(UCODE_TEMPLATE)
# Flags  9: positive overflow 1, negative overflow 0, zero 0, negative 1
f09 = deepcopy(UCODE_TEMPLATE)
# Flags 10: positive overflow 0, negative overflow 1, zero 0, negative 1
f10 = deepcopy(UCODE_TEMPLATE)
# Flags 11: positive overflow 1, negative overflow 1, zero 0, negative 1
f11 = deepcopy(UCODE_TEMPLATE)
# Flags 12: positive overflow 0, negative overflow 0, zero 1, negative 1
f12 = deepcopy(UCODE_TEMPLATE)
# Flags 13: positive overflow 1, negative overflow 0, zero 1, negative 1
f13 = deepcopy(UCODE_TEMPLATE)
# Flags 14: positive overflow 0, negative overflow 1, zero 1, negative 1
f14 = deepcopy(UCODE_TEMPLATE)
# Flags 15: positive overflow 1, negative overflow 1, zero 1, negative 1
f15 = deepcopy(UCODE_TEMPLATE)

microinstructions = [f00, f01, f02, f03, f04, f05, f06, f07, f08, f09, f10, f11, f12, f13, f14, f15]


# Create raw bytes
ucode_bytes = []

for address in range(2**17):
    # Decode address
    # As the Greenliant chip has A0-A7, A12, A15 and A16 on the L side, it is advantageous to
    # use as many of these address lines so it's easy to hook the chip to a bus. Byte select and
    # the unused address lines should therefore move to the R side.
    #
    # Chip side                LLLLLLLLRRRRLRRLL
    # Bit number               01234567890123456
    # Bus number               012345678XXX9X01X
    # instruction = (address & 0b11111000000000000) >> 12
    # step =        (address & 0b00000111100000000) >> 8
    # byte_sel =    (address & 0b00000000011000000) >> 6
    # unused1 =     (address & 0b00000000000100000) >> 5
    # flags1 =      (address & 0b00000000000010000) >> 1  # Just correct for the unused bit on the right
    # unused2 =     (address & 0b00000000000001000) >> 3
    # flags2 =      (address & 0b00000000000000111)
    # flags = flags1 + flags2

    instruction = (address & 0b00000000000011111)
    step =        (address & 0b00000000111100000) >> 5
    byte_sel =    (address & 0b00000011000000000) >> 9
    unused1 =     (address & 0b00000100000000000) >> 11
    flags1 =      (address & 0b00001000000000000) >> 12  # Just correct for the unused bit on the right
    unused2 =     (address & 0b00010000000000000) >> 13
    flags2 =      (address & 0b11100000000000000) >> 13  # As one bit is still needed for flags1
    flags = flags1 + flags2

    # Get micro-instruction
    uinstruction = microinstructions[flags][instruction][step]

    # Get byte: byte 0 is LSB
    byte = (uinstruction >> (byte_sel * 8)) & 255
    ucode_bytes.append(byte)
    print(flags)

template_loader = jinja2.FileSystemLoader(".")
env = jinja2.Environment(loader=template_loader)
template = env.get_template("control_logic.j2")
output = template.render(ucode_bytes=ucode_bytes, arraysize=2**14)
with open("control_logic.ino", "w") as fp:
    fp.write(output)
