import json
import os
import sys


class Instruction: #class for the instruction (its split into label, opcode, operand, comment)

    def __str__(self):
        return f"\t{self.label}\t{self.opcode}\t{self.operand}\t{self.comment}"

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

if len(sys.argv) < 3:
    print("Please provide 2 file names as command line arguments ex:(python main.py sample1.asm intermediate2.mdt)")
    sys.exit(1)

opcode_map = {}
SYMTAB = {}
instructions = []
error_flag = 0
if os.path.exists(sys.argv[1]):
    source_file = open(sys.argv[1],'r')
else:
    error_flag = 1
    print("Path for source code file incorrect")
    sys.exit(1)

if not os.path.exists("OPTAB.txt"):
    error_flag = 1
    print("OPTAB file doesn't exist")
    sys.exit(1)

intermediate_file = open(sys.argv[2],'w')
SYMTAB_file = open("SYMTAB.txt",'w')

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

if not instructions[0].opcode == 'START': #Read first line
        sys.exit(1)
else:
        start_address = int(instructions[0].operand,16)
        loc_ctr = start_address
        intermediate_file.write(f"{hex(loc_ctr)}\t{instructions[0]}\n")

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
            instructions[i].label = "\t"
        intermediate_file.write(f"{hex(loc_ctr)}\t{instructions[i]}\n")
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


print("---------------Program info------------------")
print("Program name:",program_name)
print("Program length:",hex(program_length))
print("Location counter",hex(loc_ctr))

print("-------------------SYMTAB--------------------")
for key, value in SYMTAB.items():
    print(f'{key}: {value}\n')
    SYMTAB_file.write(f'{key}: {value}\n')






