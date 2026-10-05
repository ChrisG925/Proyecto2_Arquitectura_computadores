# Copyright 2026 Universidad de los Andes.
# Licensed under the Solderpad Hardware License, Version 0.51 (the "License");
# you may not use this file except in compliance with the License.
# SPDX-License-Identifier: SHL-0.51
#
# Course: Arquitectura de Computadores (2026)
#
# Authors:
# - Nicolás Villegas <navillegas@miuandes.cl>

TOP := game_top
PCF := goboard.pcf

SRC := $(wildcard ./rtl/*.v ./rtl/**/*.v)

GAME_S := sw/game.s
ASSEMBLER := sw/assembler.py
GAME_HEX := sw/game.hex

JSON := $(TOP).json
ASC := $(TOP).asc
BIN := $(TOP).bin

.PHONY: all game prog clean stats

all: prog

game: $(GAME_HEX)

$(GAME_HEX): $(GAME_S) $(ASSEMBLER)
	cd sw && python assembler.py game.s game.hex

$(JSON): $(SRC) $(GAME_HEX)
	yosys -p "read_verilog $(SRC); synth_ice40 -top $(TOP) -json $(TOP).json; stat"

$(ASC): $(JSON) $(PCF)
	nextpnr-ice40 --hx1k --package vq100 --json $(JSON) --pcf $(PCF) --asc $(ASC)

$(BIN): $(ASC)
	icepack $(ASC) $(BIN)

prog: $(BIN)
	iceprog $(BIN)

clean:
	rm -f $(JSON) $(ASC) $(BIN)