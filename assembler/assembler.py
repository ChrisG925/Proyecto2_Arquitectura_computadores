import sys
import re

REGISTERS = {f"x{i}": i for i in range(16)}


def register_number(reg):
    reg = reg.lower().strip()

    if reg not in REGISTERS:
        raise ValueError(f"Registro inválido: {reg}")

    return REGISTERS[reg]


def parse_number(value):
    value = value.strip()

    if value.lower().startswith("-0x"):
        return -int(value[3:], 16)

    if value.lower().startswith("0x"):
        return int(value, 16)

    if value.lower().startswith("-0b"):
        return -int(value[3:], 2)

    if value.lower().startswith("0b"):
        return int(value, 2)

    return int(value, 10)


def check_signed(value, bits, name="inmediato"):
    minimum = -(1 << (bits - 1))
    maximum = (1 << (bits - 1)) - 1

    if value < minimum or value > maximum:
        raise ValueError(
            f"{name} {value} fuera del rango de {bits} bits "
            f"({minimum} a {maximum})"
        )


def check_unsigned(value, bits, name="inmediato"):
    minimum = 0
    maximum = (1 << bits) - 1

    if value < minimum or value > maximum:
        raise ValueError(
            f"{name} {value} fuera del rango de {bits} bits "
            f"({minimum} a {maximum})"
        )


def encode_r(opcode, rd, funct3, rs1, rs2, funct7):
    return (
        ((funct7 & 0x7F) << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )


def encode_i(opcode, rd, funct3, rs1, imm):
    check_signed(imm, 12)

    imm &= 0xFFF

    return (
        (imm << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )


def encode_shift_i(opcode, rd, funct3, rs1, shamt, funct7):
    check_unsigned(shamt, 5, "shamt")

    return (
        ((funct7 & 0x7F) << 25)
        | ((shamt & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )


def encode_s(opcode, funct3, rs1, rs2, imm):
    check_signed(imm, 12)

    imm &= 0xFFF

    imm_low = imm & 0x1F
    imm_high = (imm >> 5) & 0x7F

    return (
        (imm_high << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | (imm_low << 7)
        | (opcode & 0x7F)
    )


def encode_b(opcode, funct3, rs1, rs2, imm):
    if imm % 2 != 0:
        raise ValueError("El offset de un branch debe ser múltiplo de 2")

    if imm < -4096 or imm > 4094:
        raise ValueError(f"Offset de branch fuera de rango: {imm}")

    imm &= 0x1FFF

    bit12 = (imm >> 12) & 0x1
    bit11 = (imm >> 11) & 0x1
    bits10_5 = (imm >> 5) & 0x3F
    bits4_1 = (imm >> 1) & 0xF

    return (
        (bit12 << 31)
        | (bits10_5 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | (bits4_1 << 8)
        | (bit11 << 7)
        | (opcode & 0x7F)
    )


def encode_u(opcode, rd, imm20):
    if imm20 < 0:
        imm20 &= 0xFFFFF

    if imm20 > 0xFFFFF:
        raise ValueError(f"Inmediato U demasiado grande: {imm20}")

    return (
        ((imm20 & 0xFFFFF) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )


def encode_j(opcode, rd, imm):
    if imm % 2 != 0:
        raise ValueError("El offset de JAL debe ser múltiplo de 2")

    if imm < -1048576 or imm > 1048574:
        raise ValueError(f"Offset de JAL fuera de rango: {imm}")

    imm &= 0x1FFFFF

    bit20 = (imm >> 20) & 0x1
    bits10_1 = (imm >> 1) & 0x3FF
    bit11 = (imm >> 11) & 0x1
    bits19_12 = (imm >> 12) & 0xFF

    return (
        (bit20 << 31)
        | (bits10_1 << 21)
        | (bit11 << 20)
        | (bits19_12 << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )


def clean_line(line):
    return line.split("#")[0].strip()


def tokenize(line):
    return [
        token
        for token in re.split(r"[\s,]+", line.strip())
        if token
    ]


def parse_memory_operand(text):
    match = re.fullmatch(
        r"([-+]?(?:0x[0-9a-fA-F]+|0b[01]+|\d+))\((x\d+)\)",
        text.strip(),
        re.IGNORECASE
    )

    if not match:
        raise ValueError(f"Operando de memoria inválido: {text}")

    return parse_number(match.group(1)), match.group(2)


def first_pass(lines):
    labels = {}
    instructions = []
    pc = 0

    for line_number, original_line in enumerate(lines, start=1):
        line = clean_line(original_line)

        if not line:
            continue

        if line.startswith("."):
            continue

        while ":" in line:
            label, rest = line.split(":", 1)
            label = label.strip()

            if not label:
                raise ValueError(
                    f"Línea {line_number}: etiqueta vacía"
                )

            if label in labels:
                raise ValueError(
                    f"Línea {line_number}: etiqueta duplicada '{label}'"
                )

            labels[label] = pc
            line = rest.strip()

            if not line:
                break

        if not line:
            continue

        instructions.append((pc, line_number, line))
        pc += 4

    return labels, instructions


def assemble_instruction(line, pc, labels):
    tokens = tokenize(line)

    if not tokens:
        return None

    op = tokens[0].lower()

    if op == "lui":
        if len(tokens) != 3:
            raise ValueError("Sintaxis: lui rd, imm")

        return encode_u(
            0x37,
            register_number(tokens[1]),
            parse_number(tokens[2])
        )

    if op == "auipc":
        if len(tokens) != 3:
            raise ValueError("Sintaxis: auipc rd, imm")

        return encode_u(
            0x17,
            register_number(tokens[1]),
            parse_number(tokens[2])
        )

    immediate_operations = {
        "addi":  (0x13, 0b000),
        "slti":  (0x13, 0b010),
        "sltiu": (0x13, 0b011),
        "xori":  (0x13, 0b100),
        "ori":   (0x13, 0b110),
        "andi":  (0x13, 0b111),
    }

    if op in immediate_operations:
        if len(tokens) != 4:
            raise ValueError(f"Sintaxis: {op} rd, rs1, imm")

        opcode, funct3 = immediate_operations[op]

        return encode_i(
            opcode,
            register_number(tokens[1]),
            funct3,
            register_number(tokens[2]),
            parse_number(tokens[3])
        )

    shift_operations = {
        "slli": (0b001, 0b0000000),
        "srli": (0b101, 0b0000000),
        "srai": (0b101, 0b0100000),
    }

    if op in shift_operations:
        if len(tokens) != 4:
            raise ValueError(f"Sintaxis: {op} rd, rs1, shamt")

        funct3, funct7 = shift_operations[op]

        return encode_shift_i(
            0x13,
            register_number(tokens[1]),
            funct3,
            register_number(tokens[2]),
            parse_number(tokens[3]),
            funct7
        )

    register_operations = {
        "add":  (0b000, 0b0000000),
        "sub":  (0b000, 0b0100000),
        "sll":  (0b001, 0b0000000),
        "slt":  (0b010, 0b0000000),
        "sltu": (0b011, 0b0000000),
        "xor":  (0b100, 0b0000000),
        "srl":  (0b101, 0b0000000),
        "sra":  (0b101, 0b0100000),
        "or":   (0b110, 0b0000000),
        "and":  (0b111, 0b0000000),
    }

    if op in register_operations:
        if len(tokens) != 4:
            raise ValueError(f"Sintaxis: {op} rd, rs1, rs2")

        funct3, funct7 = register_operations[op]

        return encode_r(
            0x33,
            register_number(tokens[1]),
            funct3,
            register_number(tokens[2]),
            register_number(tokens[3]),
            funct7
        )

    load_operations = {
        "lb":  0b000,
        "lh":  0b001,
        "lw":  0b010,
        "lbu": 0b100,
        "lhu": 0b101,
    }

    if op in load_operations:
        if len(tokens) != 3:
            raise ValueError(f"Sintaxis: {op} rd, offset(rs1)")

        offset, base = parse_memory_operand(tokens[2])

        return encode_i(
            0x03,
            register_number(tokens[1]),
            load_operations[op],
            register_number(base),
            offset
        )

    store_operations = {
        "sb": 0b000,
        "sh": 0b001,
        "sw": 0b010,
    }

    if op in store_operations:
        if len(tokens) != 3:
            raise ValueError(f"Sintaxis: {op} rs2, offset(rs1)")

        offset, base = parse_memory_operand(tokens[2])

        return encode_s(
            0x23,
            store_operations[op],
            register_number(base),
            register_number(tokens[1]),
            offset
        )

    branch_operations = {
        "beq":  0b000,
        "bne":  0b001,
        "blt":  0b100,
        "bge":  0b101,
        "bltu": 0b110,
        "bgeu": 0b111,
    }

    if op in branch_operations:
        if len(tokens) != 4:
            raise ValueError(f"Sintaxis: {op} rs1, rs2, label")

        target = tokens[3]

        if target in labels:
            offset = labels[target] - pc
        else:
            offset = parse_number(target)

        return encode_b(
            0x63,
            branch_operations[op],
            register_number(tokens[1]),
            register_number(tokens[2]),
            offset
        )

    if op == "jal":
        if len(tokens) != 3:
            raise ValueError("Sintaxis: jal rd, label")

        target = tokens[2]

        if target in labels:
            offset = labels[target] - pc
        else:
            offset = parse_number(target)

        return encode_j(
            0x6F,
            register_number(tokens[1]),
            offset
        )

    if op == "jalr":
        if len(tokens) != 4:
            raise ValueError("Sintaxis: jalr rd, rs1, imm")

        return encode_i(
            0x67,
            register_number(tokens[1]),
            0b000,
            register_number(tokens[2]),
            parse_number(tokens[3])
        )

    raise ValueError(f"Instrucción no soportada: {op}")


def assemble_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    labels, instructions = first_pass(lines)

    machine_code = []

    for pc, line_number, line in instructions:
        try:
            instruction = assemble_instruction(
                line,
                pc,
                labels
            )

            machine_code.append(instruction)

        except Exception as error:
            print()
            print("ERROR DE ASSEMBLY")
            print("-----------------")
            print(f"Línea {line_number}:")
            print(f"    {line}")
            print()
            print(error)
            print()

            sys.exit(1)

    with open(output_file, "w", encoding="utf-8") as file:
        for instruction in machine_code:
            file.write(
                f"{instruction & 0xFFFFFFFF:08x}\n"
            )

    print()
    print("Assembly completado correctamente.")
    print(f"Entrada : {input_file}")
    print(f"Salida  : {output_file}")
    print(f"Labels  : {len(labels)}")
    print(f"Instr.  : {len(machine_code)}")
    print()


def main():
    if len(sys.argv) != 3:
        print(
            "Uso: python assembler/assembler.py "
            "sw/game.s sw/game.hex"
        )
        sys.exit(1)

    assemble_file(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()