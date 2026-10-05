.section .text
.global _start

_start:
    lui  x2, 0x80000

    addi x9,  x0, 0
    addi x11, x0, 0

wait_start_press:
    lw   x3, 8(x2)
    beq  x3, x0, wait_start_press

    lw   x1, 12(x2)

wait_start_release:
    lw   x3, 8(x2)
    bne  x3, x0, wait_start_release

start_round:
    addi x4, x0, 15
    sw   x4, 4(x2)

    lw   x6, 12(x2)
    lui  x5, 0x04C00

wait_3s:
    lw   x7, 12(x2)
    sub  x8, x7, x6
    bge  x8, x5, choose_target
    jal  x0, wait_3s

choose_target:
    lw   x7, 12(x2)
    xor  x1, x1, x7

    lui  x5, 0x00300
    and  x3, x1, x5

    beq  x3, x0, target_led1

    lui  x5, 0x00100
    beq  x3, x5, target_led2

    lui  x5, 0x00200
    beq  x3, x5, target_led3

target_led4:
    addi x4, x0, 8
    jal  x0, show_target

target_led1:
    addi x4, x0, 1
    jal  x0, show_target

target_led2:
    addi x4, x0, 2
    jal  x0, show_target

target_led3:
    addi x4, x0, 4

show_target:
    sw   x4, 4(x2)

    lw   x6, 12(x2)

wait_button:
    lw   x3, 8(x2)

    beq  x3, x0, wait_button

    beq  x3, x4, correct

    jal  x0, start_round

correct:
    lw   x7, 12(x2)

    sub  x8, x7, x6

    xor  x1, x1, x7
    xor  x1, x1, x6

    lui  x5, 0x262
    addi x5, x5, 1440

    addi x4,  x0, 0
    addi x12, x0, 0

conversion_loop:
    bge  x8, x5, conversion_sub
    jal  x0, conversion_done

conversion_sub:
    sub  x8, x8, x5
    addi x12, x12, 1

    addi x4, x4, 1

    andi x3, x4, 15
    addi x6, x0, 10
    beq  x3, x6, conversion_bcd_adjust

    jal  x0, conversion_loop

conversion_bcd_adjust:
    addi x4, x4, 6
    jal  x0, conversion_loop

conversion_done:
    sw   x4, 0(x2)

    add  x11, x11, x12

    addi x9, x9, 1

wait_release:
    lw   x3, 8(x2)
    bne  x3, x0, wait_release

    addi x10, x0, 10
    bge  x9, x10, final_wait_start

    jal  x0, start_round

final_wait_start:
    lw   x6, 12(x2)

    lui  x5, 0x01800

final_wait:
    lw   x7, 12(x2)
    sub  x8, x7, x6
    bge  x8, x5, final_average
    jal  x0, final_wait

final_average:
    addi x4, x0, 0
    addi x5, x0, 10

average_loop:
    bge  x11, x5, average_sub
    jal  x0, average_done

average_sub:
    sub  x11, x11, x5

    addi x4, x4, 1

    andi x3, x4, 15
    addi x6, x0, 10
    beq  x3, x6, average_bcd_adjust

    jal  x0, average_loop

average_bcd_adjust:
    addi x4, x4, 6
    jal  x0, average_loop

average_done:
    sw   x4, 0(x2)

stop:
    jal  x0, stop