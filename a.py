def builtin_encode(funcname):
    return funcname[::-1]
globals_, locals_ = ({}, {})
exec('', globals_, locals_)
temp_dict = {}
chars = ['_', '_', 'b', 'u', 'i', 'l', 't', 'i', 'n', 's', '_', '_']
builtins_str = ''.join(chars)
for k, v in globals_[builtins_str].items():
    temp_dict[builtin_encode(k)] = v
    temp_dict[k] = None
globals_['__builtins__'].update(temp_dict)

def func(a=3):
    return a
print(func())