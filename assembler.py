import os

#Sabit değişkenleri tanımlama kısmı
MAX_LABEL_LEN = 20
SYMTAB_SIZE = 100
LINE_LEN = 100
OPTAB_SIZE = 59

#Sembol, opcode ve literal tablosu için sınıflar
class Symbol:
    def __init__(self, label, address):
        self.label = label
        self.address = address

class Opcode:
    def __init__(self, opcode, code):
        self.opcode = opcode
        self.code = code

class Literal:
    def __init__(self, literal, address=None):
        self.literal = literal
        self.address = address
        self.written = False

#global değişkenler
symtab = []
optab = []
literaltab = []
locctr = 0
startAddress = 0
programLength = 0
section_table = {}
current_section = 'DEFAULT'

#Pass1 fonksiyonları
def readOptab():
    global optab
    opcode_path = os.path.join(os.path.dirname(__file__), 'opcode.txt')
    with open(opcode_path, "r") as fp:
        for line in fp:
            parts = line.split()
            if len(parts) == 2:
                optab.append(Opcode(parts[0], parts[1]))

def searchSymtab(label):
    global symtab
    for sym in symtab:
        if sym.label == label:
            return sym.address
    return None

def insertSymtab(label, locctr):
    global symtab
    if len(symtab) < SYMTAB_SIZE and searchSymtab(label) is None:
        symtab.append(Symbol(label, locctr))
    else:
        print(f"Hata: Sembolden bir tane daha var {label}")

def writeSymtab():
    global symtab
    with open("symtab.txt", "w") as fp:
        for sym in symtab:
            fp.write(f"{sym.address:04X} {sym.label}\n")

def writeIntermediate(address, label, opcode, operand):
    with open("intermediate.txt", "a") as fp:
        fp.write(f"{address:04X} {label or ''} {opcode} {operand or ''}\n")

def isOpcode(opcode):
    global optab
    for op in optab:
        if op.opcode == opcode:
            return True
    return False

def insertLiteral(literal):
    global literaltab
    for lit in literaltab:
        if lit.literal == literal:
            return
    literaltab.append(Literal(literal))

def writeLiterals():
    global locctr, literaltab
    with open("intermediate.txt", "a") as fp:
        for lit in literaltab:
            if not lit.written:
                lit.address = locctr
                size = 0
                if lit.literal.startswith("X'"):
                    size = (len(lit.literal) - 3) // 2
                elif lit.literal.startswith("C'"):
                    size = len(lit.literal) - 3
                locctr += size
                fp.write(f"{lit.address:04X} * {lit.literal}\n")
                lit.written = True

def processLine(line):
    global locctr, startAddress, current_section
    parts = line.split()
    label = None
    opcode = None
    operand = None

    #etiket olup olmadığına karar verme kısmı
    if len(parts) > 0 and not isOpcode(parts[0]) and parts[0] not in ["START", "END", "ORG", "EQU", "LTORG", "USE"]:
        label = parts[0]
        parts = parts[1:]

    #opcode olup olmadığına karar verme kısmı
    if len(parts) > 0:
        opcode = parts[0]

    
    if len(parts) > 1:
        operand = parts[1]

    if opcode == "START":
        startAddress = int(operand, 16)
        locctr = startAddress
        section_table[current_section] = locctr
        writeIntermediate(locctr, label, opcode, operand)
        return

    if opcode == "END":
        writeLiterals()
        writeIntermediate(locctr, label, opcode, operand)
        return

    if opcode == "ORG":
        locctr = int(operand, 16)
        writeIntermediate(locctr, label, opcode, operand)
        return

    if opcode == "LTORG":
        writeLiterals()
        return

    if opcode == "USE":
        section_table[current_section] = locctr
        current_section = operand if operand else "DEFAULT"
        locctr = section_table.get(current_section, 0)
        writeIntermediate(locctr, label, opcode, operand)
        return

    if opcode == "EQU":
        if operand.startswith("0x") or operand.startswith("0X"):
            value = int(operand, 16)
        else:
            value = int(operand) if operand.isdigit() else searchSymtab(operand)
        insertSymtab(label, value)
        writeIntermediate(locctr, label, opcode, operand)
        return

    if label and searchSymtab(label) is None:
        insertSymtab(label, locctr)

    if opcode:
        if operand and operand.startswith('='):
            insertLiteral(operand)

        if opcode.startswith('+'):
            if isOpcode(opcode[1:]):
                writeIntermediate(locctr, label, opcode, operand)
                locctr += 4  #format4 4 byte diye 4 arttırdık.
            else:
                print(f"Hata: geçersiz opcode {opcode}")
        elif isOpcode(opcode):
            writeIntermediate(locctr, label, opcode, operand)
            locctr += 3  #format3 = 3 byte
        elif opcode == "WORD":
            writeIntermediate(locctr, label, opcode, operand)
            locctr += 3  #bir kelime 3 bytedır.
        elif opcode == "RESW":
            writeIntermediate(locctr, label, opcode, operand)
            locctr += 3 * int(operand)  
        elif opcode == "RESB":
            writeIntermediate(locctr, label, opcode, operand)
            locctr += int(operand) 
        elif opcode == "BYTE":
            writeIntermediate(locctr, label, opcode, operand)
            if operand.startswith('X'):
                locctr += (len(operand) - 3) // 2  
            elif operand.startswith('C'):
                locctr += len(operand) - 3  
        else:
            if not isOpcode(opcode) and searchSymtab(opcode) is None:
                insertSymtab(opcode, locctr)
                locctr += 3

def processInputFile(filename):
    with open("intermediate.txt", "w") as f:  #Intermediate dosyasını temizleyerek açıyoruz
        pass

    with open(filename, "r") as file:
        for line in file:
            if line.startswith('.') or len(line.strip()) == 0:
                continue
            processLine(line.strip())

def pass1(input_file):
    global locctr, startAddress, programLength
    locctr = 0
    startAddress = 0
    readOptab()
    processInputFile(input_file)
    writeSymtab()
    programLength = locctr - startAddress
    return programLength

#Pass2 için global değişkenler
symtab_dict = {}
optab_dict = {}
intermediate = []

#Pass2 için gerekli fonksiyonlar
def readOptabPass2():
    global optab_dict
    opcode_path = os.path.join(os.path.dirname(__file__), 'opcode.txt')
    with open(opcode_path, "r") as fp:
        for line in fp:
            parts = line.split()
            if len(parts) == 2:
                optab_dict[parts[0]] = parts[1]

def readSymtabPass2():
    global symtab_dict
    with open("symtab.txt", "r") as fp:
        for line in fp:
            parts = line.split()
            if len(parts) == 2:
                symtab_dict[parts[1]] = int(parts[0], 16)

def readIntermediate():
    global intermediate
    with open("intermediate.txt", "r") as fp:
        for line in fp:
            intermediate.append(line.strip())

def split_line(line):
    parts = line.split()
    address = parts[0]
    label = ""
    opcode = ""
    operand = ""
    
    if len(parts) == 2:
        opcode = parts[1]
    elif len(parts) == 3:
        opcode, operand = parts[1], parts[2]
    elif len(parts) == 4:
        label, opcode, operand = parts[1], parts[2], parts[3]

    return address, label, opcode, operand

def pass2():
    global locctr, startAddress, programLength
    locctr = startAddress
    object_program = []
    text_record = []
    header_record = ""
    end_record = ""
    text_record_start_address = 0
    text_record_size = 0

    for line in intermediate:
        address, label, opcode, operand = split_line(line)
        address = int(address, 16)

        if opcode == "START":
            startAddress = int(operand, 16)
            locctr = startAddress
            programName = label
            header_record = f"H^{programName:<6}^{startAddress:06X}^{programLength:06X}"
            continue
        elif opcode == "END":
            end_record = f"E^{symtab_dict.get(operand, startAddress):06X}"
            continue

        object_code = ""
        if opcode in optab_dict:
            if opcode == "RSUB":
                object_code = f"{optab_dict[opcode]}0000"
            else:
                if operand and operand.startswith('#'):
                    operand_value = symtab_dict.get(operand[1:], None)
                    if operand_value is None:
                        try:
                            operand_value = int(operand[1:])
                        except ValueError:
                            print(f"Hata: geçersiz operand {operand}")
                            continue
                    object_code = f"{optab_dict[opcode]}{operand_value:04X}"
                elif operand and operand.startswith('='):
                    literal = next((lit for lit in literaltab if lit.literal == operand), None)
                    if literal is None:
                        print(f"Hata: geçersiz literal {operand}")
                        continue
                    object_code = f"{optab_dict[opcode]}{literal.address:04X}"
                elif operand:
                    operand_address = symtab_dict.get(operand, None)
                    if operand_address is None:
                        print(f"Hata: geçersiz operand {operand}")
                        continue
                    object_code = f"{optab_dict[opcode]}{operand_address:04X}"
        elif opcode.startswith('+') and opcode[1:] in optab_dict:
            operand_address = symtab_dict.get(operand, 0)
            object_code = f"{optab_dict[opcode[1:]]}1{operand_address:05X}"
        elif opcode == "BYTE":
            if operand.startswith('X'):
                object_code = operand[2:-1]
            elif operand.startswith('C'):
                object_code = ''.join(format(ord(c), 'X') for c in operand[2:-1])
        elif opcode == "WORD":
            object_code = f"{int(operand):06X}"

        if object_code:
            if text_record_size + len(object_code) // 2 > 30:
                object_program.append(f"T^{text_record_start_address:06X}^{text_record_size:02X}^{'^'.join(text_record)}")
                text_record = []
                text_record_size = 0

            if text_record_size == 0:
                text_record_start_address = address
            text_record.append(object_code)
            text_record_size += len(object_code) // 2

        locctr = address + (4 if opcode.startswith('+') else 3)

    if text_record:
        object_program.append(f"T^{text_record_start_address:06X}^{text_record_size:02X}^{'^'.join(text_record)}")

    object_program.insert(0, header_record)
    object_program.append(end_record)
    return object_program

def writeObjectProgram(object_program):
    with open("object.txt", "w") as fp:
        for record in object_program:
            fp.write(record + '\n')

if __name__ == "__main__":
    program_length = pass1("input.txt")
    print(f"Program Uzunlugu = {program_length:X}")
    
    #Pass 2
    readOptabPass2()
    readSymtabPass2()
    readIntermediate()
    programLength = program_length 
    object_program = pass2()
    writeObjectProgram(object_program)
    for record in object_program:
        print(record)
