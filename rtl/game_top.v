
// Este módulo conecta el Pochoco SoC con los botones, LEDs y displays
// de la Go Board. También carga game.hex en la memoria del SoC,
// que contiene el programa que ejecutará el procesador para el juego.

module game_top (
    // Clock de 25 MHz
    input  wire       i_Clk,

    // LEDs
    output wire [3:0] o_LED,

    // botoneras
    input  wire [3:0] i_Switch,

    // Display de 7 segmentos 1
    output wire       o_Segment1_A,
    output wire       o_Segment1_B,
    output wire       o_Segment1_C,
    output wire       o_Segment1_D,
    output wire       o_Segment1_E,
    output wire       o_Segment1_F,
    output wire       o_Segment1_G,

    // Display de 7 segmentos 2
    output wire       o_Segment2_A,
    output wire       o_Segment2_B,
    output wire       o_Segment2_C,
    output wire       o_Segment2_D,
    output wire       o_Segment2_E,
    output wire       o_Segment2_F,
    output wire       o_Segment2_G,

    // SPI
    input  wire       i_SPI_CS_n,
    input  wire       i_SPI_MOSI,
    output wire       o_SPI_MISO,
    input  wire       i_SPI_SCLK
);

    

    pochoco_soc #(
        .NumWords(512),
        .MemFile("sw/game.hex")
    ) u_pochoco_soc (

        // Clock
        .i_Clk(i_Clk),

        // LEDs y botones
        .o_LED(o_LED),
        .i_Switch(i_Switch),

        // Display 1
        .o_Segment1_A(o_Segment1_A),
        .o_Segment1_B(o_Segment1_B),
        .o_Segment1_C(o_Segment1_C),
        .o_Segment1_D(o_Segment1_D),
        .o_Segment1_E(o_Segment1_E),
        .o_Segment1_F(o_Segment1_F),
        .o_Segment1_G(o_Segment1_G),

        // Display 2
        .o_Segment2_A(o_Segment2_A),
        .o_Segment2_B(o_Segment2_B),
        .o_Segment2_C(o_Segment2_C),
        .o_Segment2_D(o_Segment2_D),
        .o_Segment2_E(o_Segment2_E),
        .o_Segment2_F(o_Segment2_F),
        .o_Segment2_G(o_Segment2_G),

        // SPI
        .i_SPI_SCLK(i_SPI_SCLK),
        .i_SPI_MOSI(i_SPI_MOSI),
        .i_SPI_CS_n(i_SPI_CS_n),
        .o_SPI_MISO(o_SPI_MISO)
    );

endmodule