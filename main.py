import json
import os
import sys
from collections import OrderedDict


class Instruction:  # class for the instruction (its split into label, opcode, operand, comment)

    def __str__(self):
        label_str = f"{self.label:<11}" if self.label else " " * 11
        return f"{label_str}{self.opcode:<5}{' ' * 5}{self.operand:<20}{self.comment:<41}"

    def __init__(self, line):
        self.label = ''
        self.opcode = ''
        self.operand = ''
        self.comment = ''

        line = line.rstrip('\n')

        # Parse label
        label_end = 10
        if line[:label_end].strip():
            self.label = line[:label_end].strip()

        # Parse opcode
        opcode_start = 11
        opcode_end = 20
        if line[opcode_start:opcode_end].strip():
            self.opcode = line[opcode_start:opcode_end].strip()

        # Parse operand
        operand_start = 21
        operand_end = 39
        if line[operand_start:operand_end].strip():
            self.operand = line[operand_start:operand_end].strip()

        # Parse comment
        comment_start = 40
        if line[comment_start:].strip():
            self.comment = line[comment_start:].strip()


class Instruction_with_address:

    def __str__(self):
        label_str = f"{self.label:<11}" if self.label else " " * 11
        return f"{self.address:<7}{label_str}{self.opcode:<5}{' ' * 5}{self.operand:<20}{self.comment:<41}"

    def __init__(self, line):
        self.address = ''
        self.label = ''
        self.opcode = ''
        self.operand = ''
        self.comment = ''

        line = line.rstrip('\n')

        # Parse address
        address_end = 6
        if line[:address_end].strip():
            self.address = line[:address_end].strip()

        # Parse label
        label_start = 7
        label_end = 15
        if line[label_start:label_end].strip():
            self.label = line[label_start:label_end].strip()

        # Parse opcode
        opcode_start = 16
        opcode_end = 25
        if line[opcode_start:opcode_end].strip():
            self.opcode = line[opcode_start:opcode_end].strip()

        # Parse operand
        operand_start = 26
        operand_end = 44
        if line[operand_start:operand_end].strip():
            self.operand = line[operand_start:operand_end].strip()

        # Parse comment
        comment_start = 45
        if line[comment_start:].strip():
            self.comment = line[comment_start:].strip()


if len(sys.argv) < 3:
    print("Please provide 2 file names as command line arguments ex:(python main.py sample1.asm intermediate2.mdt)")
    sys.exit(1)

opcode_map = {}
SYMTAB = {}
instructions = []
instructions_intermediate = []
error_flag = 0
if os.path.exists(sys.argv[1]):
    source_file = open(sys.argv[1], 'r')
else:
    error_flag = 1
    print("Path for source code file incorrect")
    sys.exit(1)

if not os.path.exists("OPTAB.txt"):
    error_flag = 1
    print("OPTAB file doesn't exist")
    sys.exit(1)

intermediate_file = open(sys.argv[2], 'w')
SYMTAB_file = open("SYMTAB.txt", 'w')
object_file = open("object.obj", 'w')
listing_file = open("list.lst", 'w')

with (open(sys.argv[1], 'r') as f):
    for line in f:
        if line.startswith("."):
            continue
        instructions.append(Instruction(line))

with open('OPTAB.txt') as op_tab:
    next(op_tab)
    next(op_tab)
    for line in op_tab:
        if not line.strip():
            continue
        mnemonic, opcode = line.split()
        opcode_map[mnemonic] = opcode

if not instructions[0].opcode == 'START':  # Read first line
    sys.exit(1)
else:
    start_address = int(instructions[0].operand, 16)
    loc_ctr = start_address
    intermediate_file.write(f"{hex(loc_ctr)}\t{instructions[0].__str__()}\n")

for i in range(1, len(instructions)):
    if instructions[i].opcode == 'END':
        break
    else:
        if instructions[i].label:
            if instructions[i].label in SYMTAB:
                error_flag = 1
                print("Error: Duplicate symbol")
                sys.exit(1)
            else:
                SYMTAB[instructions[i].label] = hex(loc_ctr)
        if not instructions[i].label:
            instructions[i].label = ""
        intermediate_file.write(f"{hex(loc_ctr)}\t{instructions[i].__str__()}\n")
        if instructions[i].opcode in opcode_map:
            loc_ctr += 3
        elif instructions[i].opcode == 'WORD':
            loc_ctr += 3
        elif instructions[i].opcode == 'RESW':
            loc_ctr += 3 * int(instructions[i].operand)
        elif instructions[i].opcode == 'RESB':
            loc_ctr += int(instructions[i].operand)
        elif instructions[i].opcode == 'BYTE':
            if instructions[i].operand[0] == 'C':
                length = len(instructions[i].operand) - 3
                loc_ctr += length
            elif instructions[i].operand[0] == 'X':
                length = (len(instructions[i].operand) - 3) // 2
                loc_ctr += length
        else:
            error_flag = 1
            print("Invalid OPCODE", instructions[i].opcode)
program_length = loc_ctr - int(instructions[0].operand)
program_name = instructions[0].label
intermediate_file.write(f"{hex(loc_ctr)}\t{instructions[len(instructions) - 1].__str__()}\n")
intermediate_file.close()

# ------------------------------PASS 2 ------------------------------------
with (open(sys.argv[2], 'r') as f):
    for line in f:
        instructions_intermediate.append(Instruction_with_address(line))

PC = 0
text_record = ''
header_record = 'H' + program_name + PC.to_bytes(3, byteorder='big').hex() + program_length.to_bytes(3,
                                                                                                     byteorder='big').hex()
object_file.write(header_record + '\n')

for i in range(0, len(instructions_intermediate)):

    error_flag = 0
    # listing_file.write(instructions_intermediate[i].__str__())
    object_code = ''
    if instructions_intermediate[i].opcode in opcode_map:
        opcode_value = opcode_map[instructions_intermediate[i].opcode]
        if not instructions_intermediate[i].operand:
            operand_address = 0
        elif instructions_intermediate[i].operand in SYMTAB:
            operand_address = int(SYMTAB[instructions_intermediate[i].operand], 16)
        else:
            error_flag = 1
            operand_address = 0
        object_code = opcode_value + operand_address.to_bytes(3, byteorder='big').hex()

    elif instructions_intermediate[i].opcode == 'BYTE':
        constant = instructions_intermediate[i].operand[2:-1]

        if instructions_intermediate[i].operand[0] == 'X':
            object_code = constant
        elif instructions_intermediate[i].operand[0] == 'C':
            object_code = constant.encode().hex()
    elif opcode == 'WORD':
        constant = int(instructions_intermediate[i].operand)
        object_code = constant.to_bytes(3, byteorder='big').hex()
    else:
        error_flag = 1

    if len(text_record) + len(object_code) <= 60:
        if object_code:
            text_record += object_code + '^'
        else:
            text_record += object_code

    else:
        text_record_length = len(text_record) // 2
        text_record_header = 'T' + PC.to_bytes(3, byteorder='big').hex() + '^' + text_record_length.to_bytes(1,
                                                                                                             byteorder='big').hex() + '^'
        object_file.write(text_record_header + text_record + '\n')

        PC += text_record_length
        text_record = object_code

    instructions_intermediate[i].comment = object_code
    listing_file.write(instructions_intermediate[i].__str__() + '\n')

text_record_length = len(text_record) // 2
text_record_header = 'T' + PC.to_bytes(3, byteorder='big').hex() + '^' + text_record_length.to_bytes(1,
                                                                                                     byteorder='big').hex() + '^'
object_file.write(text_record_header + text_record + '\n')

end_record = 'E' + int(SYMTAB['FIRST'][2:], 16).to_bytes(3, byteorder='big').hex()
object_file.write(end_record + '\n')

listing_file.close()

print("---------------Program info------------------")
print("Program name:", program_name)
print("Program length:", hex(program_length))
print("Location counter", hex(loc_ctr))

print("-------------------SYMTAB--------------------")
for key, value in SYMTAB.items():
    print(f'{key}: {value}\n')
    SYMTAB_file.write(f'{key}: {value}\n')
