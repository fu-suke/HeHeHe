from pprint import pprint

# globals_ = {}
# locals_ = {}
# exec("", globals_, locals_)
# temp_dict = {}
# for k, v in globals_["__builtins__"].items():
#     temp_dict[f"my{k}"] = v
#     temp_dict[k] = None
# globals_["__builtins__"].update(temp_dict)


# # pprint(g["__builtins__"])

# try:
#     print("abc")
# except myZeroDivisionError:
#     myprint("ZeroDivisionError")
# except myTypeError:
#     myprint("TypeError")

from builtin_encode import builtin_encode

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


for k, v in globals_[builtin_str].items():
    temp_dict[builtin_encode(k)] = v
    temp_dict[k] = None
globals_[builtin_str].update(temp_dict)

# print(ord("0"))  # 48
# print(ord("1"))  # 49
# print(ord("へ"))  # 12408
# print(ord("ヘ"))  # 12504
# print(ord("ほ"))  # 12411
# print(ord("げ"))  # 12370


"""
0 ('__name__', 'builtins')
1 ('__doc__', "Built-in functions, exceptions, and other objects.\n\nNoteworthy: None is the `nil' object; Ellipsis represents `...' in slices.")    
2 ('__package__', '')
3 ('__loader__', <class '_frozen_importlib.BuiltinImporter'>)
4 ('__spec__', ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>, origin='built-in'))
5 ('__build_class__', <built-in function __build_class__>)
6 ('__import__', <built-in function __import__>)
7 ('abs', <built-in function abs>)
8 ('all', <built-in function all>)
9 ('any', <built-in function any>)
10 ('ascii', <built-in function ascii>)
11 ('bin', <built-in function bin>)
12 ('breakpoint', <built-in function breakpoint>)
13 ('callable', <built-in function callable>)
14 ('chr', <built-in function chr>)
15 ('compile', <built-in function compile>)
16 ('delattr', <built-in function delattr>)
17 ('dir', <built-in function dir>)
18 ('divmod', <built-in function divmod>)
19 ('eval', <built-in function eval>)
20 ('exec', <built-in function exec>)
21 ('format', <built-in function format>)
22 ('getattr', <built-in function getattr>)
23 ('globals', <built-in function globals>)
24 ('hasattr', <built-in function hasattr>)
25 ('hash', <built-in function hash>)
26 ('hex', <built-in function hex>)
27 ('id', <built-in function id>)
28 ('input', <built-in function input>)
29 ('isinstance', <built-in function isinstance>)
30 ('issubclass', <built-in function issubclass>)
31 ('iter', <built-in function iter>)
32 ('aiter', <built-in function aiter>)
33 ('len', <built-in function len>)
34 ('locals', <built-in function locals>)
35 ('max', <built-in function max>)
36 ('min', <built-in function min>)
37 ('next', <built-in function next>)
38 ('anext', <built-in function anext>)
39 ('oct', <built-in function oct>)
40 ('ord', <built-in function ord>)
41 ('pow', <built-in function pow>)
42 ('print', <built-in function print>)
43 ('repr', <built-in function repr>)
44 ('round', <built-in function round>)
45 ('setattr', <built-in function setattr>)
46 ('sorted', <built-in function sorted>)
47 ('sum', <built-in function sum>)
48 ('vars', <built-in function vars>)
49 ('None', None)
50 ('Ellipsis', Ellipsis)
51 ('NotImplemented', NotImplemented)
52 ('False', False)
53 ('True', True)
54 ('bool', <class 'bool'>)
55 ('memoryview', <class 'memoryview'>)
56 ('bytearray', <class 'bytearray'>)
57 ('bytes', <class 'bytes'>)
58 ('classmethod', <class 'classmethod'>)
59 ('complex', <class 'complex'>)
60 ('dict', <class 'dict'>)
61 ('enumerate', <class 'enumerate'>)
62 ('filter', <class 'filter'>)
63 ('float', <class 'float'>)
64 ('frozenset', <class 'frozenset'>)
65 ('property', <class 'property'>)
66 ('int', <class 'int'>)
67 ('list', <class 'list'>)
68 ('map', <class 'map'>)
69 ('object', <class 'object'>)
70 ('range', <class 'range'>)
71 ('reversed', <class 'reversed'>)
72 ('set', <class 'set'>)
73 ('slice', <class 'slice'>)
74 ('staticmethod', <class 'staticmethod'>)
75 ('str', <class 'str'>)
76 ('super', <class 'super'>)
77 ('tuple', <class 'tuple'>)
78 ('type', <class 'type'>)
79 ('zip', <class 'zip'>)
"""
