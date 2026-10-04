.section .text
.global _start

_start:
    lui  x2, 0x80000
    addi x2, x2, 12

    lui  x3, 0x80000
    addi x3, x3, 4

    lui  x9, 0x80000
    addi x9, x9, 8

    addi x4, x0, 15
    sw   x4, 0(x3)

    lw   x6, 0(x2)

    lui  x5, 0x4787
    addi x5, x5, -1856

wait_3s:
    lw   x7, 0(x2)
    sub  x8, x7, x6
    bge  x8, x5, target
    jal  x0, wait_3s

target:
    addi x4, x0, 1
    sw   x4, 0(x3)

wait_button:
    lw   x10, 0(x9)
    addi x11, x0, 1
    beq  x10, x11, correct
    jal  x0, wait_button

correct:
    addi x4, x0, 0
    sw   x4, 0(x3)

stop:
    jal x0, stop