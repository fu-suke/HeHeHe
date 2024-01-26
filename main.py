from obfuscator import Obfuscator
import ast


def main():
    with open("src.py", "r", encoding="utf-8") as f:
        code = f.read()

    o = Obfuscator(
        code,
        encrypt_variables=True,
        encrypt_consts=True,
        encrypt_builtins=False,
    )
    with open("dst.py", "w", encoding="utf-8") as f:
        f.write(o.obfuscate())
    # print(o.defined_functions)
    # print(o.defined_attributes)
    # print(o.builtin_dict)
    # print(o.encrypted_constants)
    # print(o.encrypt_dict)
    # print(o.convert_to_bin_name("abc"))


if __name__ == "__main__":
    main()
