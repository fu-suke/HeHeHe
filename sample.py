
import ast
globals_, locals_ = {}, {}
exec("", globals_, locals_)
temp_dict = {}

for k, v in globals_.items():
    builtin_str = k
builtins_ = list(globals_[builtin_str].items())
builtin_chr = builtins_[14][1]
builtin_enumerate = builtins_[61][1]
builtin_list = builtins_[67][1]
builtin_range = builtins_[70][1]


def builtin_encode(builtin_funcName):
    binary = "".join(["".join([builtin_chr(48) if (byte >> i) & 1 == 0 else builtin_chr(49) for i in builtin_range(
        7, -1, -1)]) for byte in builtin_funcName.encode()])
    return "".join([builtin_chr(12411) if b == builtin_chr(48) else builtin_chr(12370) for b in binary])

class fuga():
    pass

for k, v in globals_[builtin_str].items():
    temp_dict[builtin_encode(k)] = v
globals_[builtin_str].update(temp_dict)

import math

class hoge():
    pass

