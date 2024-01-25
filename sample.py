from pprint import pprint

globals_ = {}
locals_ = {}
exec("", globals_, locals_)
temp_dict = {}
for k, v in globals_["__builtins__"].items():
    temp_dict[f"my{k}"] = v
    temp_dict[k] = None
globals_["__builtins__"].update(temp_dict)


# pprint(g["__builtins__"])

try:
    print("abc")
except myZeroDivisionError:
    myprint("ZeroDivisionError")
except myTypeError:
    myprint("TypeError")
