import sys
class Parser:
    def __init__(self, fname):
        self._fname = fname
        self._lines = ["EMPT"]
        with open(fname, 'r') as f:
            for line in f.read().split('\n'):
                self._lines.append(line)
        for i in range(1, len(self._lines)):
                self._lines[i] = self._lines[i].split(" ")
        # Same as Program for this stuff, but now we want to parse
        # so essentially we wanna expand out functions referenced by others
        regMax = 0
        for i in range(1, len(self._lines)):
            if self._lines[i][0][0] not in '0123456789':
                continue
            lreg = int(self._lines[i][1])
            rreg = int(self._lines[i][2])
            regMax = max(lreg, max(rreg, regMax))
        self._reg_max = regMax
        # Now we know what to start additional registers needed for functions
        # at, and we just need to do string parsing basically
        # this is good for now, run other funcs
    def read_external_func(self, fname):
        # Returns the "self._lines" for this other func
        # ***ASSUMES OTHER FUNC IS TOTALLY REDUCED
        lines = []
        with open(fname, 'r') as f:
            for line in f.read().split('\n'):
                lines.append(line)
        for i in range(len(lines)):
                lines[i] = lines[i].split(" ")

        regMax = 0
        for i in range(len(lines)):
            lreg = int(lines[i][1])
            rreg = int(lines[i][2])
            regMax = max(lreg, max(rreg, regMax))

        return (lines, regMax)        

    def copy_reg(self, line_start, reg1, reg2, intermediate):
        # Writes the lines that copy reg1 contents to reg2 using intermediate
        l = str(line_start+1)
        r1 = str(reg1)
        r2 = str(reg2)
        interm = str(intermediate)
        l1 = l + " " + interm + " " + interm + " " + l
        l = str(line_start+2)
        l2 = l + " " + interm + " " + r1 + " " + l
        l = str(line_start+3)
        l3 = l + " " + r2 + " " + r2 + " " + l
        l = str(line_start+4)
        l4 = l + " " + r2 + " " + interm + " " + l
        return ([l1, l2, l3, l4], int(l))
    
    def parse_line(self, line):
        l1 = line[0]
        x = line[1]
        y = line[2]
        l2 = line[3]
        return (int(l1), int(x), int(y), int(l2))

    def delete_reg(self, line_number, reg1):
        l = str(line_number+1)
        r1 = str(reg1)
        line = l + " " + r1 + " " + r1 + " " + l
        return (line, int(l))

    def parse_one_func(self, line_number):
        # Essentially we just want to rename the registers inside the file
        # copy the designated input regs over to 1...n for n inputs
        # Re-route the line #'s within and after the function
        # and slide it into our func, then at end re-write everything
        # and copy output over. We allocate one extra register as an
        # "in-between" used for copying
        intermediate = self._reg_max + 1
        curReg = intermediate + 1
        funcLine = self._lines[line_number]
        fname = funcLine[0]
        all_lines = []
        i_sep = funcLine.index(':')
        j_sep = funcLine[i_sep + 1 : ].index(':') + i_sep + 1
        for i in funcLine[1:funcLine.index(':')]:
            coplines,newline = \
                    self.copy_reg(line_number, int(i), curReg, intermediate)
            all_lines += coplines
            line_number = newline
            curReg = curReg + 1
        # Need to figure out outputRegs
        outputRegInFunc = map(int, funcLine[i_sep+1:j_sep]) #in og function
        outputRegInFuncNEW = [i for i in outputRegInFunc]
        newOutputsMapped = map(int, funcLine[j_sep + 1:]) # want to map to
        if len(outputRegInFunc) != len(newOutputsMapped):
            print("FATAL ERROR: outputs mapped wrong")
            return -1
        
        # above has now added a lot of lines copying our initial values over
        # now we have everything in the right inputs, but new reg #'s, adding
        # to intermediate actually
        line_counter = line_number
        line_number -= 1
        func_lines,maxReg = self.read_external_func(fname)
        for line in func_lines:
            # We add line_number to everything (subbed one so addition works)
            # And we add intermediate to all regs
            l1,x,y,l2 = self.parse_line(line)
            l1 = l1 + line_number
            l2 = l2 + line_number
            if x in outputRegInFunc:
                i = outputRegInFunc.index(x)
                outputRegInFuncNEW[i] = x + intermediate
            if y in outputRegInFunc:
                i = outputRegInFunc.index(y)
                outputRegInFuncNEW[i] = y + intermediate
            x = x + intermediate if x != 0 else 0
            y = y + intermediate if y != 0 else 0
            newl = str(l1) + " " + str(x) + " " + str(y) + " " + str(l2)
            all_lines.append(newl)
            line_counter += 1
        # Now need to copy everything from outputRegInFuncNEW to newOutputsMap..
        for i,j in zip(outputRegInFuncNEW, newOutputsMapped):
            if i == j:
                continue
            coplines,newline = self.copy_reg(line_counter, i, j, intermediate)
            all_lines += coplines
            line_counter = newline
        for i in range(0, maxReg+1):
            j = i + intermediate
            line,newline = self.delete_reg(line_counter, j)
            all_lines.append(line)
            line_counter = newline
        # Now we have modified this sufficiently, but outside program needs to
        # change other line numbers, so need to return which num to add
        # to everything
        for i in range(len(all_lines)):
                all_lines[i] = all_lines[i].split(" ")
        return all_lines
        


    def parse(self):
        i = 1
        while True:
            if i >= len(self._lines):
                return self._lines
            line = self._lines[i]
            if line[0][0] in "0123456789":
                i = i + 1
                continue
            new_lines = self.parse_one_func(i)
            additive = len(new_lines) - 1
            earlyline = [self._lines[0]]
            for j in range(1, i):
                if self._lines[j][0][0] not in "0123456789":
                    earlyline.append(self._lines[j])
                    continue
                l1,x,y,l2 = self.parse_line(self._lines[j])
                l1 = l1 + additive if l1 > i else l1
                l2 = l2 + additive if l2 > i else l2
                line = str(l1) + " "+str(x)+" "+str(y)+" "+ str(l2)
                earlyline.append(line.split(" "))
            laterline = []
            for j in range(i+1, len(self._lines)):
                if self._lines[j][0][0] not in "0123456789":
                    laterline.append(self._lines[j])
                    continue
                l1,x,y,l2 = self.parse_line(self._lines[j])
                l1 = l1 + additive if l1 > i else l1
                l2 = l2 + additive if l2 > i else l2
                line = str(l1) + " "+str(x)+" "+str(y)+" "+ str(l2)
                laterline.append(line.split(" "))
            self._lines = earlyline + new_lines + laterline


if __name__ == '__main__':
    input_name = sys.argv[1]
    output_name = sys.argv[2]
    p = Parser(input_name)
    lines = p.parse()
    with open(output_name, 'w') as f:
        for i in range(1, len(lines)-1):
            f.write(reduce(lambda x,y: x+" "+y, lines[i])+'\n')
        f.write(reduce(lambda x,y: x+" "+y, lines[len(lines)-1]))
    