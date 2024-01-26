def builtin_encode(builtin_funcName):
    binary = "".join(["".join(['0' if (byte >> i) & 1 == 0 else '1' for i in range(
        7, -1, -1)]) for byte in builtin_funcName.encode()])
    return "".join(['ほ' if b == '0' else 'げ' for b in binary])


# print(ord("0"))  # 48
# print(ord("1"))  # 49
# print(ord("へ"))  # 12408
# print(ord("ヘ"))  # 12504
# print(ord("ほ"))  # 12411
# print(ord("げ"))  # 12370
