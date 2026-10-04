.section .text
.global _start

_start:
    lui  x2, 0x80000
    addi x2, x2, 12

    lui  x3, 0x80000
    addi x3, x3, 4

    addi x4, x0, 15
    sw   x4, 0(x3)

    lw   x6, 0(x2)

    lui  x5, 0x4787
    addi x5, x5, -1856

wait:
    lw   x7, 0(x2)
    sub  x8, x7, x6
    bge  x8, x5, done
    jal  x0, wait

done:
    addi x4, x0, 0
    sw   x4, 0(x3)

stop:
    jal x0, stop