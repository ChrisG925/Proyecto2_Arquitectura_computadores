import sys
import re


def parse_reg(token):
    token = token.strip()

    if not token.startswith("x"):
        raise ValueError(f"Registro invalido: {token}")

    n = int(token[1:])

    if n < 0 or n > 15:
        raise ValueError(f"RV32E solo permite x0-x15: {token}")

    return n


def parse_imm(token):
    return int(token.strip(), 0)


def check_signed(value, bits, name):
    minimum = -(1 << (bits - 1))
    maximum = (1 << (bits - 1)) - 1

    if value < minimum or value > maximum:
        raise ValueError(
            f"{name} fuera de rango para {bits} bits: {value}"
        )


def encode_lui(rd, imm20):
    if imm20 < 0 or imm20 > 0xFFFFF:
        raise ValueError(f"Inmediato LUI fuera de rango: {imm20}")

    return (
        ((imm20 & 0xFFFFF) << 12)
        | ((rd & 0x1F) << 7)
        | 0x37
    )


def encode_addi(rd, rs1, imm):
    check_signed(imm, 12, "ADDI")

    return (
        ((imm & 0xFFF) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x0 << 12)
        | ((rd & 0x1F) << 7)
        | 0x13
    )


def encode_andi(rd, rs1, imm):
    check_signed(imm, 12, "ANDI")

    return (
        ((imm & 0xFFF) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x7 << 12)
        | ((rd & 0x1F) << 7)
        | 0x13
    )


def encode_add(rd, rs1, rs2):
    return (
        (0x00 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x0 << 12)
        | ((rd & 0x1F) << 7)
        | 0x33
    )


def encode_sub(rd, rs1, rs2):
    return (
        (0x20 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x0 << 12)
        | ((rd & 0x1F) << 7)
        | 0x33
    )


def encode_xor(rd, rs1, rs2):
    return (
        (0x00 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x4 << 12)
        | ((rd & 0x1F) << 7)
        | 0x33
    )


def encode_and(rd, rs1, rs2):
    return (
        (0x00 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x7 << 12)
        | ((rd & 0x1F) << 7)
        | 0x33
    )


def encode_or(rd, rs1, rs2):
    return (
        (0x00 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x6 << 12)
        | ((rd & 0x1F) << 7)
        | 0x33
    )


def encode_lw(rd, rs1, imm):
    check_signed(imm, 12, "LW")

    return (
        ((imm & 0xFFF) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x2 << 12)
        | ((rd & 0x1F) << 7)
        | 0x03
    )


def encode_sw(rs2, rs1, imm):
    check_signed(imm, 12, "SW")

    imm &= 0xFFF

    imm11_5 = (imm >> 5) & 0x7F
    imm4_0 = imm & 0x1F

    return (
        (imm11_5 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | (0x2 << 12)
        | (imm4_0 << 7)
        | 0x23
    )


def encode_branch(rs1, rs2, offset, funct3):
    if offset % 2 != 0:
        raise ValueError(f"Branch no alineado: {offset}")

    check_signed(offset, 13, "Branch")

    offset &= 0x1FFF

    imm12 = (offset >> 12) & 0x1
    imm10_5 = (offset >> 5) & 0x3F
    imm4_1 = (offset >> 1) & 0xF
    imm11 = (offset >> 11) & 0x1

    return (
        (imm12 << 31)
        | (imm10_5 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | (imm4_1 << 8)
        | (imm11 << 7)
        | 0x63
    )


def encode_beq(rs1, rs2, offset):
    return encode_branch(rs1, rs2, offset, 0x0)


def encode_bne(rs1, rs2, offset):
    return encode_branch(rs1, rs2, offset, 0x1)


def encode_bge(rs1, rs2, offset):
    return encode_branch(rs1, rs2, offset, 0x5)


def encode_jal(rd, offset):
    if offset % 2 != 0:
        raise ValueError(f"JAL no alineado: {offset}")

    check_signed(offset, 21, "JAL")

    offset &= 0x1FFFFF

    imm20 = (offset >> 20) & 0x1
    imm10_1 = (offset >> 1) & 0x3FF
    imm11 = (offset >> 11) & 0x1
    imm19_12 = (offset >> 12) & 0xFF

    return (
        (imm20 << 31)
        | (imm10_1 << 21)
        | (imm11 << 20)
        | (imm19_12 << 12)
        | ((rd & 0x1F) << 7)
        | 0x6F
    )


def clean_line(line):
    line = line.split("#", 1)[0]
    return line.strip()


def tokenize(line):
    line = line.replace(",", " ")
    return line.split()


def parse_mem_operand(text):
    match = re.fullmatch(
        r"([+-]?(?:0x[0-9a-fA-F]+|\d+))\((x\d+)\)",
        text
    )

    if not match:
        raise ValueError(f"Operando de memoria invalido: {text}")

    imm = parse_imm(match.group(1))
    rs1 = parse_reg(match.group(2))

    return imm, rs1


def first_pass(lines):
    labels = {}
    instructions = []

    pc = 0

    for lineno, raw in enumerate(lines, start=1):
        line = clean_line(raw)

        if not line:
            continue

        if line.startswith("."):
            continue

        while ":" in line:
            label, rest = line.split(":", 1)
            label = label.strip()

            if not label:
                raise ValueError(
                    f"Linea {lineno}: etiqueta vacia"
                )

            if label in labels:
                raise ValueError(
                    f"Linea {lineno}: etiqueta duplicada {label}"
                )

            labels[label] = pc

            line = rest.strip()

            if not line:
                break

        if not line:
            continue

        if line.startswith("."):
            continue

        instructions.append((pc, lineno, line))
        pc += 4

    return labels, instructions


def resolve_target(token, labels, pc):
    if token in labels:
        return labels[token] - pc

    return parse_imm(token)


def assemble_instruction(line, labels, pc):
    tokens = tokenize(line)

    if not tokens:
        return None

    op = tokens[0].lower()

    if op == "lui":
        if len(tokens) != 3:
            raise ValueError("Sintaxis: lui rd, imm")

        rd = parse_reg(tokens[1])
        imm = parse_imm(tokens[2])

        return encode_lui(rd, imm)

    if op == "addi":
        if len(tokens) != 4:
            raise ValueError("Sintaxis: addi rd, rs1, imm")

        rd = parse_reg(tokens[1])
        rs1 = parse_reg(tokens[2])
        imm = parse_imm(tokens[3])

        return encode_addi(rd, rs1, imm)

    if op == "andi":
        if len(tokens) != 4:
            raise ValueError("Sintaxis: andi rd, rs1, imm")

        rd = parse_reg(tokens[1])
        rs1 = parse_reg(tokens[2])
        imm = parse_imm(tokens[3])

        return encode_andi(rd, rs1, imm)

    if op in ("add", "sub", "xor", "and", "or"):
        if len(tokens) != 4:
            raise ValueError(
                f"Sintaxis: {op} rd, rs1, rs2"
            )

        rd = parse_reg(tokens[1])
        rs1 = parse_reg(tokens[2])
        rs2 = parse_reg(tokens[3])

        if op == "add":
            return encode_add(rd, rs1, rs2)

        if op == "sub":
            return encode_sub(rd, rs1, rs2)

        if op == "xor":
            return encode_xor(rd, rs1, rs2)

        if op == "and":
            return encode_and(rd, rs1, rs2)

        return encode_or(rd, rs1, rs2)

    if op == "lw":
        if len(tokens) != 3:
            raise ValueError("Sintaxis: lw rd, imm(rs1)")

        rd = parse_reg(tokens[1])
        imm, rs1 = parse_mem_operand(tokens[2])

        return encode_lw(rd, rs1, imm)

    if op == "sw":
        if len(tokens) != 3:
            raise ValueError("Sintaxis: sw rs2, imm(rs1)")

        rs2 = parse_reg(tokens[1])
        imm, rs1 = parse_mem_operand(tokens[2])

        return encode_sw(rs2, rs1, imm)

    if op in ("beq", "bne", "bge"):
        if len(tokens) != 4:
            raise ValueError(
                f"Sintaxis: {op} rs1, rs2, etiqueta"
            )

        rs1 = parse_reg(tokens[1])
        rs2 = parse_reg(tokens[2])
        offset = resolve_target(tokens[3], labels, pc)

        if op == "beq":
            return encode_beq(rs1, rs2, offset)

        if op == "bne":
            return encode_bne(rs1, rs2, offset)

        return encode_bge(rs1, rs2, offset)

    if op == "jal":
        if len(tokens) != 3:
            raise ValueError(
                "Sintaxis: jal rd, etiqueta"
            )

        rd = parse_reg(tokens[1])
        offset = resolve_target(tokens[2], labels, pc)

        return encode_jal(rd, offset)

    raise ValueError(
        f"Instruccion no soportada: {op}"
    )


def assemble(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    labels, instructions = first_pass(lines)

    machine_code = []

    for pc, lineno, line in instructions:
        try:
            instruction = assemble_instruction(
                line,
                labels,
                pc
            )
        except Exception as e:
            raise RuntimeError(
                f"{input_file}:{lineno}: {e}\n"
                f"    {line}"
            )

        machine_code.append(instruction)

    with open(output_file, "w", encoding="utf-8") as f:
        for instruction in machine_code:
            f.write(f"{instruction:08x}\n")

    print(f"Assembler OK")
    print(f"Entrada: {input_file}")
    print(f"Salida:  {output_file}")
    print(f"Instrucciones: {len(machine_code)}")

    if labels:
        print("Etiquetas:")

        for name, address in labels.items():
            print(f"  {name}: 0x{address:08x}")


if __name__ == "__main__":
    input_file = "game.s"
    output_file = "game.hex"

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]

    try:
        assemble(input_file, output_file)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)