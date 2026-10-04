import sys
def encode_jal(rd, offset):
    offset &= 0x1fffff

    imm20 = (offset >> 20) & 0x1
    imm10_1 = (offset >> 1) & 0x3ff
    imm11 = (offset >> 11) & 0x1
    imm19_12 = (offset >> 12) & 0xff

    return (
        (imm20 << 31)
        | (imm10_1 << 21)
        | (imm11 << 20)
        | (imm19_12 << 12)
        | ((rd & 0x1f) << 7)
        | 0x6f
    )


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


def encode_and(rd, rs1, rs2):
    return (
        (0x00 << 25)
        | ((rs2 & 0x1f) << 20)
        | ((rs1 & 0x1f) << 15)
        | (0x7 << 12)
        | ((rd & 0x1f) << 7)
        | 0x33
    )

def encode_beq(rs1, rs2, offset):
    offset &= 0x1fff

    imm12 = (offset >> 12) & 0x1
    imm10_5 = (offset >> 5) & 0x3f
    imm4_1 = (offset >> 1) & 0xf
    imm11 = (offset >> 11) & 0x1

    return (
        (imm12 << 31)
        | (imm10_5 << 25)
        | ((rs2 & 0x1f) << 20)
        | ((rs1 & 0x1f) << 15)
        | (0x0 << 12)
        | (imm4_1 << 8)
        | (imm11 << 7)
        | 0x63
    )

def encode_sub(rd, rs1, rs2):
    return (
        (0x20 << 25)
        | ((rs2 & 0x1f) << 20)
        | ((rs1 & 0x1f) << 15)
        | (0x0 << 12)
        | ((rd & 0x1f) << 7)
        | 0x33
    )

def encode_bge(rs1, rs2, offset):
    offset &= 0x1fff

    imm12 = (offset >> 12) & 0x1
    imm10_5 = (offset >> 5) & 0x3f
    imm4_1 = (offset >> 1) & 0xf
    imm11 = (offset >> 11) & 0x1

    return (
        (imm12 << 31)
        | (imm10_5 << 25)
        | ((rs2 & 0x1f) << 20)
        | ((rs1 & 0x1f) << 15)
        | (0x5 << 12)
        | (imm4_1 << 8)
        | (imm11 << 7)
        | 0x63
    )

program = [
    encode_lui(2, 0x80000),

    # start_round
    encode_addi(4, 0, 15),
    encode_sw(4, 2, 4),

    # Espera inicial
    encode_lw(6, 2, 12),
    encode_lui(5, 0x04C00),

    # wait_3s
    encode_lw(7, 2, 12),
    encode_sub(8, 7, 6),
    encode_bge(8, 5, 8),
    encode_jal(0, -12),

    # LED objetivo = LED 1
    encode_addi(4, 0, 1),
    encode_sw(4, 2, 4),

    # Inicio medicion
    encode_lw(6, 2, 12),

    # wait_button
    encode_lw(3, 2, 8),
    encode_beq(3, 0, -4),

    # Boton correcto = 1
    encode_addi(5, 0, 1),
    encode_beq(3, 5, 8),

    # Incorrecto -> reiniciar ronda
    encode_jal(0, -60),

    # Tiempo final
    encode_lw(7, 2, 12),
    encode_sub(8, 7, 6),

    # 2.500.000 ciclos = 0,1 segundos
    encode_lui(5, 0x262),
    encode_addi(5, 5, 1440),

    # Contador BCD de decimas
    encode_addi(4, 0, 0),

    # conversion_loop
    encode_bge(8, 5, 8),
    encode_jal(0, 36),

    # Resta una decima
    encode_sub(8, 8, 5),
    encode_addi(4, 4, 1),

    # Ajuste BCD
    encode_andi(3, 4, 15),
    encode_addi(6, 0, 10),
    encode_beq(3, 6, 8),

    # No necesita ajuste
    encode_jal(0, -28),

    # Ajuste 09 -> 10, 19 -> 20, etc.
    encode_addi(4, 4, 6),
    encode_jal(0, -36),

    # display
    encode_sw(4, 2, 0),

    # stop
    encode_jal(0, 0),
]


with open("game.hex", "w") as f:
    for instr in program:
        f.write(f"{instr:08x}\n")

print("game.hex generado")