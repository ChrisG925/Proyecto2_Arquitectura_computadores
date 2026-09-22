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

    lui  x13, 0x4787
    addi x13, x13, -1856

    bltu x12, x13, esperar_3s


seleccionar_led:
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

    lui  x13, 0x262
    addi x13, x13, 1440


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


mostrar_tiempo:
    add  x12, x14, x0
    addi x15, x0, 0
    addi x13, x0, 10


convertir_bcd:
    bltu x12, x13, bcd_listo

    addi x12, x12, -10
    addi x15, x15, 1

    jal  x0, convertir_bcd


bcd_listo:
    andi x15, x15, 15
    andi x12, x12, 15

    slli x15, x15, 4

    or   x15, x15, x12

    sw   x15, 0(x1)


comprobar_rondas:
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
    bltu x8, x13, promedio_calculado

    addi x8, x8, -10
    addi x14, x14, 1

    jal  x0, division_promedio


promedio_calculado:
    add  x12, x14, x0

    addi x15, x0, 0
    addi x13, x0, 10


promedio_bcd:
    bltu x12, x13, promedio_listo

    addi x12, x12, -10
    addi x15, x15, 1

    jal  x0, promedio_bcd


promedio_listo:
    andi x15, x15, 15
    andi x12, x12, 15

    slli x15, x15, 4

    or   x15, x15, x12

    sw   x15, 0(x1)

    sw   x0, 0(x2)


fin:
    jal  x0, fin