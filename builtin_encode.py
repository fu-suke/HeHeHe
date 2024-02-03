def builtin_encode(builtin_funcName, ZERO, ONE, PREFIX):
    binary = "".join(["".join(['0' if (byte >> i) & 1 == 0 else '1' for i in range(
        7, -1, -1)]) for byte in builtin_funcName.encode()])
    return PREFIX + "".join([ZERO if b == '0' else ONE for b in binary])