import sys

def reg(x):
    return int(x.replace("x", ""))

def encode_lui(rd, imm20):
    return ((imm20 & 0xfffff) << 12) | ((rd & 0x1f) << 7) | 0x37

def encode_addi(rd, rs1, imm):
    return ((imm & 0xfff) << 20) | ((rs1 & 0x1f) << 15) | (0 << 12) | ((rd & 0x1f) << 7) | 0x13

def encode_andi(rd, rs1, imm):
    return ((imm & 0xfff) << 20) | ((rs1 & 0x1f) << 15) | (7 << 12) | ((rd & 0x1f) << 7) | 0x13

def encode_srli(rd, rs1, shamt):
    return ((shamt & 0x1f) << 20) | ((rs1 & 0x1f) << 15) | (5 << 12) | ((rd & 0x1f) << 7) | 0x13

def encode_lw(rd, rs1, imm):
    return ((imm & 0xfff) << 20) | ((rs1 & 0x1f) << 15) | (2 << 12) | ((rd & 0x1f) << 7) | 0x03

def encode_sw(rs2, rs1, imm):
    imm &= 0xfff
    imm11_5 = (imm >> 5) & 0x7f
    imm4_0 = imm & 0x1f
    return (imm11_5 << 25) | ((rs2 & 0x1f) << 20) | ((rs1 & 0x1f) << 15) | (2 << 12) | (imm4_0 << 7) | 0x23

program = [
    encode_lui(2, 0x80000),
    encode_addi(2, 2, 12),
    encode_lw(1, 2, 0),
    encode_srli(3, 1, 20),
    encode_andi(3, 3, 15),
    encode_lui(4, 0x80000),
    encode_addi(4, 4, 4),
    encode_sw(3, 4, 0),
]

with open("counter_test.hex", "w") as f:
    for instr in program:
        f.write(f"{instr:08x}\n")

print("counter_test.hex generado")