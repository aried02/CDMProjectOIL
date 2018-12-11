import math
import sys
# Run this file to compile one-instruction-languages
# The construct and ideas used included in help document
# File needs to have number registers used, and initial non-zero vals
# in order space separated. Line numbers are based off of including these
# first lines
# Each command is a space separated string of Line1 reg1 reg2 line2

class Program:
    def __init__(self, fname, registers=None):
        self._fname = fname
        self._lines = ["EMPT"]
        with open(fname, 'r') as f:
            for line in f.read().split('\n'):
                self._lines.append(line)
        if registers is None:
            for i in range(3, len(self._lines)):
                self._lines[i] = self._lines[i].split(" ")
            self._registers = [0 for i in range(int(self._lines[1]) + 1)]
            self._registers[0] = 1
            reg = 1
            for s in self._lines[2].split(" "):
                self._registers[reg] = int(s)
                reg = reg + 1
        else:
            for i in range(1, len(self._lines)):
                self._lines[i] = self._lines[i].split(" ")
            regMax = 0
            for i in range(1, len(self._lines)):
                lreg = int(self._lines[i][1])
                rreg = int(self._lines[i][2])
                regMax = max(lreg, max(rreg, regMax))
            self._registers =[0 for i in range(regMax + 1)]
            for i in range(len(registers)):
                self._registers[i+1] = registers[i]
            self._registers[0] = 1
            

    
    def parse_line(self, num):
        l1 = self._lines[num][0]
        x = self._lines[num][1]
        y = self._lines[num][2]
        l2 = self._lines[num][3]
        return (int(l1), int(x), int(y), int(l2))

    def push(self, prevLs, nextL):
        for i in range(len(prevLs) - 1):
            prevLs[i] = prevLs[i+1]
        prevLs[len(prevLs) - 1] = nextL
        return prevLs

    def run(self, debug, optimized, outputReg = None):
        if debug:
            print("Starting Run, initial registers:")
            print(self._registers)
            print()
        if type(self._lines[1]) != type(' '):
            nextL = 1
            bot = 1
        else:
            nextL = 3
            bot = 3
        prevLs = [-1, -1]
        while nextL >= bot and nextL < len(self._lines):
            l1,x,y,l2 = self.parse_line(nextL)
            # Check if repeat
            if optimized:
                if nextL == prevLs[-1]:
                    if debug:
                        print("Line "+ str(nextL)+" repeated, optimizing")
                    ogx = x
                    x = self._registers[x]
                    y = self._registers[y]
                    if x*y < 0 or (x == 0 and y < 0) or y == 0: #bad
                        print("INFINITE LOOP")
                        return -1
                    if x < 0:
                        x = x - (int(math.ceil(float(x)/float(y)))*y)
                    if x >= 0:
                        x = x - (x//y + 1)*y
                    self._registers[ogx] = x
                    prevLs = self.push(prevLs, nextL)
                    if x < 0:
                        nextL = l1
                    else:
                        nextL = l2
                    if debug:
                        print("Loop " + str(prevLs[-1]) +" done, registers:")
                        print(self._registers)
                        print()
                    continue
                if nextL == prevLs[-2]:
                    if debug:
                        print("Lines "+ str(nextL)+" "+ str(prevLs[-1]) + " looped, optimizing")
                    l1, x, y, l2 = self.parse_line(nextL)
                    l1p, xp, yp, l2p = self.parse_line(prevLs[-1])
                    if x == xp or x == yp or y == xp:
                        if debug:
                            print("Too hard to figure out, not reducing")
                        continue
                    # See which one flip-flops first
                    ogx, ogxp = x, xp
                    x = self._registers[x]
                    y = self._registers[y]
                    xp = self._registers[xp]
                    yp = self._registers[yp]
                    fl = x/y
                    sl = xp/yp
                    if x >= 0 or x % y != 0:
                        fl = fl + 1
                    if xp >= 0 or xp % yp != 0:
                        sl = sl + 1
                    if fl <= 0 and sl <= 0:
                        print("INFINITE LOOP")
                        return -1
                    if fl <= 0:
                        c = (sl, 2)
                    elif sl <= 0:
                        c = (fl, 1)
                    else:
                        c = min(fl, sl)
                        if c == fl:
                            c = (fl, 1)
                        else:
                            c = (sl, 2)
                    # If the first quits first, that means we run the second
                    # c - 1 times, else we run both c times
                    if c[1] == 1:
                        x = x - y*c[0]
                        xp = xp - yp*(c[0]-1)
                        prevLs = self.push(prevLs, nextL)
                        nextL = l1 if x < 0 else l2
                    else:
                        x = x - y*c[0]
                        xp = xp - yp*c[0]
                        prevLs = self.push(prevLs, nextL)
                        nextL = l1p if xp < 0 else l2p
                    self._registers[ogx] = x
                    self._registers[ogxp] = xp
                    if debug:
                        print("Loop " + str(prevLs[-2]) +" " + str(prevLs[-1]) + " done, registers:")
                        print(self._registers)
                        print()
                    continue
                    # So now c should be how many times the loop is run
                    # But gets a lil complicated cuz one is run one extra
                    # time
            # Execute line instruction if not
            self._registers[x] = self._registers[x] - self._registers[y]
            prevLs = self.push(prevLs, nextL)
            if self._registers[x] < 0:
                nextL = l1
            else:
                nextL = l2
            if debug:
                print("Instruction " + str(prevLs[-1]) + " done")
                print(self._registers)
                print()
        print("-----FINAL RESULT-----")
        if outputReg is None:
            print(self._registers)
        else:
            for i in outputReg:
                print(self._registers[i])
        return 0

    def printit(self):
        print(self._lines)
        print(self._registers)
        print(self.__finishingline)


if __name__ == "__main__":
    fname = sys.argv[1]
    debug, fast = False, True
    registers = None
    outputReg = None
    if '-d' in sys.argv or '-v' in sys.argv: #debug/verbose mode
        debug = True
    if '-s' in sys.argv: #slow mode
        fast = False
    if '-o' in sys.argv:
        left = sys.argv.index('-o') + 1
        if '(' in sys.argv[left]:
            stre = ''
            while ')' not in stre:
                stre = stre + sys.argv[left]
                left += 1
            outputReg = stre.split(",")
            outputReg[0] = outputReg[0][1:]
            outputReg[-1] = outputReg[-1][:-1]
            outputReg = map(int, outputReg)
        else:
            outputReg = [int(sys.argv[left])]
    if '-i' in sys.argv:
        left = sys.argv.index('-i') + 1
        stre = ''
        while ']' not in stre:
            stre = stre + sys.argv[left]
            left += 1
        registers = stre.split(",")
        registers[0] = registers[0][1:]
        registers[-1] = registers[-1][:-1]
        registers = map(int, registers)
    p = Program(fname, registers=registers)
    p.run(debug, fast, outputReg=outputReg)
