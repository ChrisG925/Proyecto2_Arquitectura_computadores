.section .text
.global _start

_start:
    lui  x2, 0x80000
    addi x2, x2, 12

loop:
    lw   x1, 0(x2)

    srli x3, x1, 20
    andi x3, x3, 15

    lui  x4, 0x80000
    addi x4, x4, 4

    sw   x3, 0(x4)

    jal  x0, loop