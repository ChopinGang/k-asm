# start of file

file = open("input.asm", "r")

text = file.read().split('\n')
file.close()

lineNumber = 0
endian = True
output = ""
formattedOutput = ""
errorList = {
    0x00: "unknown error",
    0x01: "immediate value may not be more than one byte/2 hex digits",
    0x02: "absolute value/address may not be more than 2 bytes/4 hex digits",
    0x03: "incorrect amount of arguments",
    0x04: "given addressing mode not available for this opcode"
}
errors = []
errorLines = []


def getErrors():
    global errors, errorList, errorLines
    strg = ""
    for i in range(0, len(errors)):
        strg += str(errorLines[i]) + ":  " + errorList.get(errors[i]) + "\n"
    return strg


def newError(val):
    global errors, errorLines, lineNumber
    errors.append(val)
    errorLines.append(lineNumber)


def push(ops):
    global output, formattedOutput
    formattedOutput += ('\t' * (8 - len(ops)))
    for i in range(0, len(ops), 2):
        output += ops[i] + "" + ops[i + 1] + " "
        formattedOutput += ops[i] + "" + ops[i + 1] + " "
    formattedOutput += "\n"


def evalNum(num):
    number = num[0]
    outputNum = ""
    addr = True
    if number[0] == '#':
        addr = False
        if number[1] == '$':
            if len(number[2:]) < 3:
                outputNum = number[2:]
            else:
                newError(0x01)
                return
        else:
            hexNum = hex(int(number[1:]))[2:]
            if len(hexNum) < 3:
                outputNum = str(hexNum)
            else:
                newError(0x01)
                return
    elif number[0] == '$':
        if len(number[1:]) < 5:
            if len(number[1:]) < 4:
                outputNum = ("0" * (4 - len(number[1:]))) + number[1:]
            else:
                outputNum = number[1:]
            if not endian:
                outputNum = outputNum[2:] + outputNum[0:2]
        else:
            newError(0x02)
            return
    elif number[0].isdigit():
        hexNum = hex(int(number))[2:]
        if len(hexNum) < 5:
            outputNum = hexNum
            if len(hexNum) < 4:
                outputNum = ("0" * (4 - len(hexNum))) + hexNum
            else:
                outputNum = hexNum
            if not endian:
                outputNum = outputNum[2:] + outputNum[0:2]
        else:
            newError(0x02)
            return
    else:
        newError(0x00)
    return outputNum, addr


class OpCode:
    def __init__(self, coder, listOfValues, addressing=[0, 1]):
        self.code = coder
        self.vals = listOfValues
        self.addr = addressing


def add(instr, opList, addrList=[-2]):
    if addrList == [-2]:
        codes.append(OpCode(instr, opList))
    else:
        codes.append(OpCode(instr, opList, addrList))


def makeCodes():
    global codes
    # opcode, list of addressing modes, numbers corresponding
    # -1:implied, 0:absolute, 1:immediate, 2:accumulator, 3:x, 4:y
    add("nop", ["ea"], [-1]); add("lda", ["ad", "a9"]); add("adc", ["6d", "69"])
    add("sta", ["8d"], [0]); add("cmp", ["cd", "c9"]); add("jmp", ["4c"], [0])
    add("and", ["2d", "29"]); add("asl", ["0a"], [-1]); add("bit", ["2c", "89"])
    add("brk", ["00"], [-1]); add("clc", ["18"], [-1]); add("cld", ["d8"], [-1])
    add("cli", ["58"], [-1]); add("clv", ["b8"], [-1]); add("cpx", ["ec", "e0"])
    add("cpy", ["cc", "c0"]); add("dec", ["ce", "3a", "ca", "88"], [0, 2, 3, 4])
    add("eor", ["4d", "49"]); add("inc", ["ee", "1a", "e8", "c8"], [0, 2, 3, 4])
    add("jsr", ["20"], [0]); add("ldx", ["ae", "a2"]); add("ldy", ["ac", "a0"])
    add("lsr", ["4e", "4a"], [0, 2]); add("ora", ["0d", "09"])
    add("pha", ["48"], [-1]); add("php", ["08"], [-1]); add("phx", ["da"], [-1])
    add("phy", ["5a"], [-1]); add("pla", ["68"], [-1]); add("plp", ["28"], [-1])
    add("plx", ["fa"], [-1]); add("ply", ["7a"], [-1]); add("rol", ["2e", "2a"], [0, 2])
    add("ror", ["6e", "6a"], [0, 2]); add("rti", ["40"], [-1]); add("rts", ["60"], [-1])
    add("sbc", ["ed", "e9", "fd", "f9"], [0, 1, 3, 4]); add("sec", ["38"], [-1])
    add("sed", ["f8"], [-1]); add("sei", ["78"], [-1])
    add("sta", ["8d", "81", "91"], [0, 3, 4]); add("stp", ["db"], [0])
    add("stx", ["8e"], [0]); add("sty", ["8c"], [0]); add("stz", ["9c"], [0])
    add("tax", ["aa"], [-1]); add("tay", ["a8"], [-1]); add("trb", ["1c"], [0])
    add("tsb", ["0c"], [0]); add("tsx", ["ba"], [-1]); add("txa", ["8a"], [-1])
    add("txs", ["9a"], [-1]); add("tya", ["98"], [-1]); add("wai", ["cb"], [-1])


codes = []
makeCodes()


def main():
    global output, formattedOutput, endian, text, errorList, lineNumber
    # main loop that goes through and changes all the opcodes to hex
    for lineU in text:
        lineNumber += 1
        # meaning line unformatted because we have to remove comments
        line = ""
        if lineU.find(';') == -1:
            line = lineU
        else:
            line = lineU[:(lineU.find(';'))]
        formattedOutput += line
        if line == "":
            continue
        tok = line.lower().split()
        # code is an opcode
        for code in codes:
            if tok[0] == code.code:
                if -1 in code.addr:
                    if len(tok) == 1:
                        push(code.vals[0])
                    else:
                        newError(0x03)
                    break
                if tok[1].lower() == "a":
                    if 2 in code.addr:
                        push(code.vals[code.addr.index(2)])
                        break
                    else:
                        newError(0x04)
                        break
                if tok[1].lower() == "x":
                    if 3 in code.addr:
                        push(code.vals[code.addr.index(3)])
                        break
                    else:
                        newError(0x04)
                        break
                if tok[1].lower() == "y":
                    if 4 in code.addr:
                        push(code.vals[code.addr.index(4)])
                        break
                    else:
                        newError(0x04)
                        break
                num, addrMode = evalNum(tok[1:])
                if addrMode:
                    if 0 in code.addr:
                        push(code.vals[0] + str(num))
                    else:
                        newError(0x04)
                    break
                else:
                    if 1 in code.addr:
                        push(code.vals[1] + str(num))
                    else:
                        newError(0x04)
                    break
            else:
                continue


main()


print(output)
print("_________________________________")
print(formattedOutput)
print("_________________________________")
print(getErrors())
