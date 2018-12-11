import math
# Run this file to compile one-instruction-languages
# The construct and ideas used included in help document
# File needs to have number registers used, and initial non-zero vals
# in order space separated. Line numbers are based off of including these
# first lines
# Each command is a space separated string of Line1 reg1 reg2 line2

class Program:
    def __init__(self, fname):
        self._fname = fname
        self._lines = ["EMPT"]
        with open(fname, 'r') as f:
            for line in f.read().split('\n'):
                self._lines.append(line)
        for i in range(3, len(self._lines)):
            self._lines[i] = self._lines[i].split(" ")
        self._registers = [0 for i in range(int(self._lines[1]) + 1)]
        self._registers[0] = 1
        reg = 1
        for s in self._lines[2].split(" "):
            self._registers[reg] = int(s)
            reg = reg + 1
    
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

    def run(self, debug, optimized):
        if debug:
            print("Starting Run, initial registers:")
            print(self._registers)
            print()
        nextL = 3
        prevLs = [-1, -1]
        while nextL >= 2 and nextL < len(self._lines):
            l1,x,y,l2 = self.parse_line(nextL)
            # Check if repeat
            if optimized:
                if nextL == prevLs[-1]:
                    if debug:
                        print("Line "+ str(nextL)+" repeated, optimizing")
                    ogx = x
                    x = self._registers[x]
                    y = self._registers[y]
                    if x*y < 0 or (x == 0 and y < 0): #bad
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
                    # Actually kinda hard now
                    print("working on it")               
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
        print(self._registers)
        return 0

    def printit(self):
        print(self._lines)
        print(self._registers)
        print(self.__finishingline)

p = Program("try.oil")
p.run(False, False)
