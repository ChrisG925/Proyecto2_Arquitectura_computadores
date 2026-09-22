.section .text
.global _start


_start:

    lui  x1, 0x80000
    addi x2, x1, 4
    addi x3, x1, 8
    addi x4, x1, 12
    addi x5, x0, 0
    addi x6, x0, 0



nueva_ronda:

    addi x12, x0, 15
    sw   x12, 0(x2)
    lw   x7, 0(x4)      

esperar_3s:

    lw   x8, 0(x4)
    sub  x12, x8, x7
    lui  x13, 0x04787
    addi x13, x13, 0x6C0
    bltu x12, x13, esperar_3s
    lw   x7, 0(x4)
    srli x12, x7, 5
    xor  x7, x7, x12
    srli x12, x7, 9
    xor  x7, x7, x12
    andi x9, x7, 3
    addi x10, x0, 1
    sll  x10, x10, x9
    sw   x10, 0(x2)
    lw   x7, 0(x4)



esperar_boton:

    lw   x11, 0(x3)
    beq  x11, x0, esperar_boton
    bne  x11, x10, error

respuesta_correcta:

    lw   x8, 0(x4)
    sub  x8, x8, x7
    addi x14, x0, 0
    lui  x13, 0x00262
    addi x13, x13, 0x5A0

convertir_decimas:

    bltu x8, x13, conversion_lista
    sub  x8, x8, x13
    addi x14, x14, 1
    jal  x0, convertir_decimas

conversion_lista:

    bne  x14, x0, tiempo_valido
    addi x14, x0, 1


tiempo_valido:

    add  x6, x6, x14
    addi x5, x5, 1
    sw   x14, 0(x1)
    addi x12, x0, 10
    beq  x5, x12, calcular_promedio



esperar_soltar:

    lw   x11, 0(x3)
    bne  x11, x0, esperar_soltar
    jal  x0, nueva_ronda



error:

    addi x12, x0, 15
    sw   x12, 0(x2)
    addi x12, x0, 238
    sw   x12, 0(x1)



error_esperar_soltar:

    lw   x11, 0(x3)
    bne  x11, x0, error_esperar_soltar
    jal  x0, nueva_ronda



calcular_promedio:

    addi x14, x0, 0
    addi x13, x0, 10
    add  x8, x6, x0


division_promedio:

    bltu x8, x13, promedio_listo
    addi x8, x8, -10
    addi x14, x14, 1
    jal  x0, division_promedio


promedio_listo:

    sw   x14, 0(x1)
    sw   x0, 0(x2)

fin:

    jal  x0, fin