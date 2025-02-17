import re

class RiscVAssembler:
    def _init_(self):
        self.REGISTER_MAP = {
            "zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011", "tp": "00100",
            "t0": "00101", "t1": "00110", "t2": "00111", "s0": "01000", "fp": "01000", "s1": "01001",
            "a0": "01010", "a1": "01011", "a2": "01100", "a3": "01101", "a4": "01110",
            "a5": "01111", "a6": "10000", "a7": "10001", "s2": "10010", "s3": "10011",
            "s4": "10100", "s5": "10101", "s6": "10110", "s7": "10111", "s8": "11000",
            "s9": "11001", "s10": "11010", "s11": "11011", "t3": "11100", "t4": "11101",
            "t5": "11110", "t6": "11111",
            }
        self.INSTRUCTION_MAP = {
            'add': ['0000000','000','0110011'], 'sub': ['0100000','000','0110011'], 'slt': ['0000000','010','0110011'],
            'srl': ['0000000','101','0110011'], 'or': ['0000000','110','0110011'], 'and': ['0000000','111','0110011'],
            'lw': ['','010','0000011'], 'jalr': ['','000','1100111'], 'addi': ['','000','0010011'], 'sw': ['','010','0100011'], 
            'beq': ['','000','1100011'], 'bne': ['','001','1100011'], 'jal': ['','','1101111']
            }
        self.label_dict = {}

    def assemble_instruction(self, instruction, pc):
        # Remove any leading/trailing whitespace
        instruction = instruction.strip()
        
        # Handle labels
        if ':' in instruction:
            label, instr = instruction.split(':', 1)
            label = label.strip()
            instr = instr.strip()
            self.label_dict[label] = pc
            instruction = instr  # Process the instruction part after the label
        
        # Parse the instruction
        parts = re.split(r'[\s,]+', instruction)
        opcode = parts[0]
        
        if opcode in self.INSTRUCTION_MAP:
            opcode_info = self.INSTRUCTION_MAP[opcode]
            opcode_bits = opcode_info[0]
            funct3 = opcode_info[1] if len(opcode_info) > 1 else "000"
            
            if opcode == "add":
                rd = self.REGISTER_MAP[parts[1]]
                rs1 = self.REGISTER_MAP[parts[2]]
                rs2 = self.REGISTER_MAP[parts[3]]
                funct7 = opcode_info[2] if len(opcode_info) > 2 else "0000000"
                machine_code = f"{funct7}{rs2}{rs1}{funct3}{rd}{opcode_bits}"
                return machine_code
            
            elif opcode == "jalr":
                rd = self.REGISTER_MAP[parts[1]]
                rs1 = self.REGISTER_MAP[parts[2]]
                imm = int(parts[3])
                imm_bits = format(imm & 0xFFF, '012b')  # 12-bit immediate
                machine_code = f"{imm_bits}{rs1}{funct3}{rd}{opcode_bits}"
                return machine_code
            
            elif opcode == "beq":
                rs1 = self.REGISTER_MAP[parts[1]]
                rs2 = self.REGISTER_MAP[parts[2]]
                offset = parts[3]
                
                # Check if the offset is a label
                if offset in self.label_dict:
                    offset_value = (self.label_dict[offset] - pc) // 4  # Branch offset is in multiples of 4
                else:
                    offset_value = int(offset)
                
                # RISC-V B-type instruction format: imm[12|10:5] rs2 rs1 funct3 imm[4:1|11] opcode
                imm = offset_value
                imm_12 = (imm >> 12) & 0x1
                imm_10_5 = (imm >> 5) & 0x3F
                imm_4_1 = (imm >> 1) & 0xF
                imm_11 = (imm >> 11) & 0x1
                
                machine_code = f"{imm_12:01b}{imm_10_5:06b}{rs2}{rs1}{funct3}{imm_4_1:04b}{imm_11:01b}{opcode_bits}"
                return machine_code
            
            else:
                raise ValueError(f"Unsupported instruction: {opcode}")
        else:
            raise ValueError(f"Unknown opcode: {opcode}")

    def assemble_program(self, instructions):
        machine_code = []
        pc = 0  # Program counter
        
        # First pass: collect labels
        for instr in instructions:
            if ':' in instr:
                label, _ = instr.split(':', 1)
                self.label_dict[label.strip()] = pc
            else:
                pc += 4  # Each instruction is 4 bytes
        
        # Second pass: assemble instructions
        pc = 0
        for instr in instructions:
            if ':' in instr:
                _, instr = instr.split(':', 1)
                instr = instr.strip()
            
            if instr:  # Skip empty lines
                machine_code.append(self.assemble_instruction(instr, pc))
                pc += 4
        
        return machine_code

    def write_output_to_file(self, machine_code, output_file):
        with open(output_file, "w") as file:
            for code in machine_code:
                file.write(code + "\n")

# Main function to read, assemble, and write output
def main():
    assembler = RiscVAssembler()
    
    # Read instructions from input.asm
    with open("/Users/dishakukkal/CO/input.asm", "r") as file:
        instructions = file.readlines()
    
    # Assemble the program
    machine_code = assembler.assemble_program(instructions)
    
    # Write the machine code to output file
    assembler.write_output_to_file(machine_code, "output.mc")
    
    # Print the machine code in binary format
    for code in machine_code:
        print(code)

if _name_ == "_main_":
    main()