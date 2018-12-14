def Ackermann(m, n):
    s = [m]
    while len(s) > 0:
        m = s.pop()
        if (m == 0 or n == 0):
            n += m + 1
        else:
            s.append(m-1)
            s.append(m)
            n = n - 1
    return n

def AckCor(m, n):
    if m == 0:
        return n+1
    if m > 0 and n == 0:
        return AckCor(m-1, 1)
    return AckCor(m-1, AckCor(m, n-1))

def A(i, n):
    s = [i, n]
    while len(s) > 1:
        ncur = s.pop()
        icur = s.pop()
        if icur == 0: s.append(ncur+1)
        elif ncur == 0:
            s.append(icur - 1)
            s.append(1)
        else:
            s.append(icur-1)
            s.append(icur)
            s.append(ncur-1)
    return s.pop()
print A(3, 8)
