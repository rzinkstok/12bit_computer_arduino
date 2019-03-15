import jinja2
from copy import deepcopy

# Signals
HLT = int('0b10000000000000000000000000000000', 2)  # Halt clock
BAI = int('0b01000000000000000000000000000000', 2)  # Bank address in
MAI = int('0b00100000000000000000000000000000', 2)  # Memory address in
RDI = int('0b00010000000000000000000000000000', 2)  # RAM data in
RDO = int('0b00001000000000000000000000000000', 2)  # RAM data out
IRI = int('0b00000100000000000000000000000000', 2)  # Instruction register in
IRO = int('0b00000010000000000000000000000000', 2)  # Instruction register out
ARI = int('0b00000001000000000000000000000000', 2)  # A register in
ARO = int('0b00000000100000000000000000000000', 2)  # A register out
BRI = int('0b00000000010000000000000000000000', 2)  # B register in
BRO = int('0b00000000001000000000000000000000', 2)  # B register out
SRO = int('0b00000000000100000000000000000000', 2)  # Sum register out
SUB = int('0b00000000000010000000000000000000', 2)  # ALU subtract
ORI = int('0b00000000000001000000000000000000', 2)  # Output register in
PCE = int('0b00000000000000100000000000000000', 2)  # Program counter enable
PCO = int('0b00000000000000010000000000000000', 2)  # Program counter out
JMP = int('0b00000000000000001000000000000000', 2)  # Jump (program counter in)
FRI = int('0b00000000000000000100000000000000', 2)  # Flags register in


# Instruction template
UCODE_TEMPLATE = [
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 0000 - NOOP
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 0001 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 0010 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 0011 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 0100 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 0101 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 0110 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 0111 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 1000 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 1001 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 1010 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 1011 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 1100 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 1101 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 1110 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 1111 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 0000 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 0001 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 0010 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 0011 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 0100 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 0101 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 0110 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 0111 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 1000 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 1001 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 1010 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 1011 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 1100 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 1101 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 1110 -
    [MAI | PCO, RDO | IRI | PCE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 1111 -
]


# Instructions per flag combination

# Flags  0: carry 0, zero 0, negative 0, overflow 0
f00 = deepcopy(UCODE_TEMPLATE)
# Flags  1: carry 0, zero 0, negative 0, overflow 1
f01 = deepcopy(UCODE_TEMPLATE)
# Flags  2: carry 0, zero 0, negative 1, overflow 0
f02 = deepcopy(UCODE_TEMPLATE)
# Flags  3: carry 0, zero 0, negative 1, overflow 1
f03 = deepcopy(UCODE_TEMPLATE)
# Flags  4: carry 0, zero 1, negative 0, overflow 0
f04 = deepcopy(UCODE_TEMPLATE)
# Flags  5: carry 0, zero 1, negative 0, overflow 1
f05 = deepcopy(UCODE_TEMPLATE)
# Flags  6: carry 0, zero 1, negative 1, overflow 0
f06 = deepcopy(UCODE_TEMPLATE)
# Flags  7: carry 0, zero 1, negative 1, overflow 1
f07 = deepcopy(UCODE_TEMPLATE)
# Flags  8: carry 1, zero 0, negative 0, overflow 0
f08 = deepcopy(UCODE_TEMPLATE)
# Flags  9: carry 1, zero 0, negative 0, overflow 1
f09 = deepcopy(UCODE_TEMPLATE)
# Flags 10: carry 1, zero 0, negative 1, overflow 0
f10 = deepcopy(UCODE_TEMPLATE)
# Flags 11: carry 1, zero 0, negative 1, overflow 1
f11 = deepcopy(UCODE_TEMPLATE)
# Flags 12: carry 1, zero 1, negative 0, overflow 0
f12 = deepcopy(UCODE_TEMPLATE)
# Flags 13: carry 1, zero 1, negative 0, overflow 1
f13 = deepcopy(UCODE_TEMPLATE)
# Flags 14: carry 1, zero 1, negative 1, overflow 0
f14 = deepcopy(UCODE_TEMPLATE)
# Flags 15: carry 1, zero 1, negative 1, overflow 1
f15 = deepcopy(UCODE_TEMPLATE)

microinstructions = [f00, f01, f02, f03, f04, f05, f06, f07, f08, f09, f10, f11, f12, f13, f14, f15]


# Create raw bytes
ucode_bytes = []

for address in range(2**15):
    flags =       (address & 0b111100000000000) >> 11
    byte_sel =    (address & 0b000011000000000) >> 9
    instruction = (address & 0b000000111110000) >> 4
    stage =       (address & 0b000000000001111)

    # Get micro-instruction
    uinstruction = microinstructions[flags][instruction][stage]

    # Get byte: byte 0 is LSB
    byte = (uinstruction >> (byte_sel * 8)) & 255
    ucode_bytes.append(byte)

n = len(ucode_bytes)//2
print(n)
ucode_bytes1 = ucode_bytes[:n]
ucode_bytes2 = ucode_bytes[n:]

template_loader = jinja2.FileSystemLoader(".")
env = jinja2.Environment(loader=template_loader)
template = env.get_template("control_logic.j2")
output = template.render(ucode_bytes1=ucode_bytes1, ucode_bytes2=ucode_bytes2)
with open("control_logic.ino", "w") as fp:
    fp.write(output)
