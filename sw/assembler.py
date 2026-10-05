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

def encode_add(rd, rs1, rs2):
    return (
        (0x00 << 25)
        | ((rs2 & 0x1f) << 20)
        | ((rs1 & 0x1f) << 15)
        | (0x0 << 12)
        | ((rd & 0x1f) << 7)
        | 0x33
    )


program = [
    # x2 = base MMIO 0x80000000
    encode_lui(2, 0x80000),

    # x9 = rondas correctas
    encode_addi(9, 0, 0),

    # x11 = suma de tiempos en decimas
    encode_addi(11, 0, 0),

    # Esperar cualquier boton para iniciar partida
    encode_lw(3, 2, 8),
    encode_beq(3, 0, -4),

    # Semilla inicial
    encode_lw(1, 2, 12),

    # Esperar que se suelte el boton
    encode_lw(3, 2, 8),
    encode_bne(3, 0, -4),

    # =====================================
    # start_round
    # =====================================

    # Cuatro LEDs encendidos
    encode_addi(4, 0, 15),
    encode_sw(4, 2, 4),

    # Inicio espera ~3.2 s
    encode_lw(6, 2, 12),
    encode_lui(5, 0x04C00),

    # wait_3s
    encode_lw(7, 2, 12),
    encode_sub(8, 7, 6),
    encode_bge(8, 5, 8),
    encode_jal(0, -12),

    # Mezclar semilla
    encode_lw(7, 2, 12),
    encode_xor(1, 1, 7),

    # Bits 20 y 21
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

    # Inicio exacto de medicion
    encode_lw(6, 2, 12),

    # =====================================
    # wait_button
    # =====================================

    encode_lw(3, 2, 8),

    # Ningun boton
    encode_beq(3, 0, -4),

    # Correcto
    encode_beq(3, 4, 8),

    # Incorrecto -> reiniciar ronda
    encode_jal(0, -116),

    # =====================================
    # correct
    # =====================================

    # Contador final
    encode_lw(7, 2, 12),

    # x8 = ciclos de respuesta
    encode_sub(8, 7, 6),

    # Actualizar semilla
    encode_xor(1, 1, 7),
    encode_xor(1, 1, 6),

    # Una decima = 2.500.000 ciclos
    encode_lui(5, 0x262),
    encode_addi(5, 5, 1440),

    # x4 = tiempo BCD
    encode_addi(4, 0, 0),

    # x12 = tiempo decimal en decimas
    encode_addi(12, 0, 0),

    # =====================================
    # conversion_loop
    # =====================================

    # Si quedan >= 0.1 s, restar una decima
    encode_bge(8, 5, 8),

    # Si quedan menos, terminar conversion
    encode_jal(0, 40),

    # Restar 0.1 s
    encode_sub(8, 8, 5),

    # Tiempo decimal++
    encode_addi(12, 12, 1),

    # BCD++
    encode_addi(4, 4, 1),

    # Revisar unidad BCD
    encode_andi(3, 4, 15),
    encode_addi(6, 0, 10),
    encode_beq(3, 6, 8),

    # Volver al conversion_loop
    encode_jal(0, -32),

    # Ajuste BCD 09 -> 10, 19 -> 20...
    encode_addi(4, 4, 6),
    encode_jal(0, -40),

    # =====================================
    # conversion_done
    # =====================================

    # Mostrar tiempo de esta ronda
    encode_sw(4, 2, 0),

    # Acumular tiempo decimal
    encode_add(11, 11, 12),

    # Una ronda correcta mas
    encode_addi(9, 9, 1),

    # Esperar que se suelte el boton
    encode_lw(3, 2, 8),
    encode_bne(3, 0, -4),

   # ¿Ya tenemos 10 correctas?
encode_addi(10, 0, 10),
encode_bge(9, 10, 8),

# No -> nueva ronda
encode_jal(0, -224),

# =====================================
# Pausa despues de la ronda 10
# =====================================

# Guardar contador inicial
encode_lw(6, 2, 12),

# Aproximadamente 1 segundo
encode_lui(5, 0x01800),

# final_wait
encode_lw(7, 2, 12),
encode_sub(8, 7, 6),
encode_bge(8, 5, 8),
encode_jal(0, -12),

# =====================================
# final_average
# =====================================

encode_addi(4, 0, 0),

    # Divisor = 10
    encode_addi(5, 0, 10),

    # =====================================
    # average_loop
    # =====================================

    # Mientras suma >= 10
    encode_bge(11, 5, 8),

    # Termino promedio
    encode_jal(0, 36),

    # suma -= 10
    encode_sub(11, 11, 5),

    # promedio BCD++
    encode_addi(4, 4, 1),

    # Revisar unidad BCD
    encode_andi(3, 4, 15),
    encode_addi(6, 0, 10),
    encode_beq(3, 6, 8),

    # Volver al average_loop
    encode_jal(0, -28),

    # Ajustar BCD
    encode_addi(4, 4, 6),
    encode_jal(0, -36),

    # =====================================
    # average_done
    # =====================================

    # Mostrar promedio final
    encode_sw(4, 2, 0),

    # Detener
    encode_jal(0, 0),
]

with open("game.hex", "w") as f:
    for instr in program:
        f.write(f"{instr:08x}\n")

print("game.hex generado")