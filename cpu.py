"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8      # Register
        self.ram = [0] * 256    # RAM
        
        self.pc = 0             # Program counter
        self.sp = 7             # Stack pointer index in the register
        self.reg[self.sp] = 244 # Stack pointer 
        self.flag = 0           # Flag 00000LGE

        self.branchtable = {}   #Branch table
        self.branchtable[130] = self.LDI
        self.branchtable[71] = self.prnt
        self.branchtable[162] = self.mul
        self.branchtable[69] = self.push
        self.branchtable[70] = self.pop
        self.branchtable[160] = self.mul2
        self.branchtable[17] = self.ret
        self.branchtable[80] = self.call
        self.branchtable[132] = self.store
        self.branchtable[167] = self.compare
        self.branchtable[84] = self.jump
        self.branchtable[86] = self.JNE
        self.branchtable[85] = self.JEQ
        self.branchtable[170] = self.OR_
        self.branchtable[171] = self.XOR_
        self.branchtable[105] = self.NOT_
        self.branchtable[172] = self.SHL
        self.branchtable[173] = self.SHR
        self.branchtable[164] = self.MOD_
        self.branchtable[168] = self.AND_


    def load(self, file_path):
        """Load a program into memory."""

        address = 0
        program = open(file_path, "r")
                        
        for line in program:
            if line[:8][0] == "0" or line[:8][0] == "1":
                self.ram[address] = int(line[:8],2)
                address += 1
        # print(self.ram)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 2
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 4

        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]

        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]

        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]

        elif op == "NOT":
            result = 0b11111111 - self.reg[reg_a]
            self.reg[reg_a] = result

        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]

        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]

        elif op == "MOD":
            if self.reg[reg_b] is not 0:
                self.reg[reg_a] %= self.reg[reg_b]
            else:
                print("Cannot preform modulus with second argument being 0")
                sys.exit(1)

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def LDI(self):
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)
        self.pc += 3

    def prnt(self):
        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2

    def mul(self):
        self.alu("MUL", self.ram_read(self.pc+1), self.ram_read(self.pc+2)) 
        self.pc +=3

    def push(self, value = None):
        self.reg[self.sp] -= 1
        if not value:
            value = self.reg[self.ram_read(self.pc + 1)]        
        # print("VALUE: ", value)
        self.ram_write(value ,self.reg[self.sp])
        self.pc += 2

    def pop(self):
        value = self.ram_read(self.reg[self.sp])
        reg_position = self.ram_read(self.pc + 1)
        self.reg[reg_position] = value
        self.reg[self.sp] += 1
        self.pc += 2

    def call(self):
        new_pc = self.reg[self.ram_read(self.pc+1)]
        self.push(self.pc + 2)
        self.pc = new_pc
        
    def mul2(self):
        self.alu("ADD", self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def ret(self):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def store(self):
        value = self.reg[self.ram_read(self.pc + 1)]
        store_index = self.ram_read(self.pc + 2)
        self.reg[store_index] = value
        self.pc += 3
    
    def compare(self):
        self.alu('CMP', self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def jump(self):
        reg_index = self.ram_read(self.pc + 1)
        value = self.reg[reg_index]
        self.pc = value

    def JNE(self):
        if ~self.flag  & 1:
            self.jump()
        else:
            self.pc += 2

    def JEQ(self):
        if self.flag & 1:
            self.jump()
        else:
            self.pc += 2

    def XOR_(self):
        self.alu('XOR', self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def OR_(self):
        self.alu('OR', self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def NOT_(self):
        self.alu('NOT', self.ram_read(self.pc+1), None)
        self.pc += 2

    def SHR(self):
        self.alu("SHR", self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def SHL(self):
        self.alu("SHL", self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def MOD_(self):
        self.alu("MOD", self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def AND_(self):
        self.alu("AND", self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3
        
    def run(self):
        """Run the CPU."""
        running = True

        while running:
            IR = self.ram_read(self.pc)
            # print(IR) 
            # print("PC: ",self.pc)   
            if IR == 1:
                running = False
            
            elif IR in self.branchtable:
                self.branchtable[IR]()
                
            else:
                print("Instruction not understood")
                sys.exit(1)

