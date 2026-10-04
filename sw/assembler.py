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
def encode_or(rd, rs1, rs2):
    return (
        (0x00 << 25)
        | ((rs2 & 0x1f) << 20)
        | ((rs1 & 0x1f) << 15)
        | (0x6 << 12)
        | ((rd & 0x1f) << 7)
        | 0x33
    )

def encode_bne(rs1, rs2, offset):
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
        | (0x1 << 12)
        | (imm4_1 << 8)
        | (imm11 << 7)
        | 0x63
    )

def encode_xor(rd, rs1, rs2):
    return (
        (0x00 << 25)
        | ((rs2 & 0x1f) << 20)
        | ((rs1 & 0x1f) << 15)
        | (0x4 << 12)
        | ((rd & 0x1f) << 7)
        | 0x33
    )


program = [
    # x2 = base MMIO 0x80000000
    encode_lui(2, 0x80000),

    # Esperar cualquier boton para iniciar partida
    encode_lw(3, 2, 8),
    encode_beq(3, 0, -4),

    # Semilla inicial
    encode_lw(1, 2, 12),

    # Esperar que se suelte el boton
    encode_lw(3, 2, 8),
    encode_bne(3, 0, -4),

    # =====================
    # start_round
    # =====================

    # Cuatro LEDs encendidos
    encode_addi(4, 0, 15),
    encode_sw(4, 2, 4),

    # Espera inicial ~3.2 s
    encode_lw(6, 2, 12),
    encode_lui(5, 0x04C00),

    # wait_3s
    encode_lw(7, 2, 12),
    encode_sub(8, 7, 6),
    encode_bge(8, 5, 8),
    encode_jal(0, -12),

    # Mezclar semilla con contador
    encode_lw(7, 2, 12),
    encode_xor(1, 1, 7),

    # Tomar bits 20 y 21
    encode_lui(5, 0x00300),
    encode_and(3, 1, 5),

    # 00 -> LED 1
    encode_beq(3, 0, 28),

    # 01 -> LED 2
    encode_lui(5, 0x00100),
    encode_beq(3, 5, 28),

    # 10 -> LED 3
    encode_lui(5, 0x00200),
    encode_beq(3, 5, 28),

    # 11 -> LED 4
    encode_addi(4, 0, 8),
    encode_jal(0, 24),

    # LED 1
    encode_addi(4, 0, 1),
    encode_jal(0, 16),

    # LED 2
    encode_addi(4, 0, 2),
    encode_jal(0, 8),

    # LED 3
    encode_addi(4, 0, 4),

    # Mostrar LED objetivo
    encode_sw(4, 2, 4),

    # Momento exacto de inicio de medicion
    encode_lw(6, 2, 12),

    # =====================
    # wait_button
    # =====================

    encode_lw(3, 2, 8),

    # Ningun boton
    encode_beq(3, 0, -4),

    # Boton correcto
    encode_beq(3, 4, 8),

    # Incorrecto -> reiniciar ronda
    encode_jal(0, -116),

    # =====================
    # correct
    # =====================

    # Contador final
    encode_lw(7, 2, 12),

    # x8 = ciclos de respuesta
    encode_sub(8, 7, 6),

    # Actualizar semilla
    encode_xor(1, 1, 7),
    encode_xor(1, 1, 6),

    # 2.500.000 ciclos = 0,1 s
    encode_lui(5, 0x262),
    encode_addi(5, 5, 1440),

    # x4 = tiempo BCD
    encode_addi(4, 0, 0),

    # conversion_loop
    encode_bge(8, 5, 8),
    encode_jal(0, 36),

    # Restar una decima
    encode_sub(8, 8, 5),
    encode_addi(4, 4, 1),

    # Ajuste BCD
    encode_andi(3, 4, 15),
    encode_addi(6, 0, 10),
    encode_beq(3, 6, 8),

    # Volver al loop
    encode_jal(0, -28),

    # Ajuste 09 -> 10, 19 -> 20, etc.
    encode_addi(4, 4, 6),
    encode_jal(0, -36),

    # Mostrar tiempo
    encode_sw(4, 2, 0),

    # Esperar que se suelte el boton
    encode_lw(3, 2, 8),
    encode_bne(3, 0, -4),

    # Siguiente ronda
    encode_jal(0, -200),
]

with open("game.hex", "w") as f:
    for instr in program:
        f.write(f"{instr:08x}\n")

print("game.hex generado")