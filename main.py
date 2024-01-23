from obfuscator import Obfuscator
# from parent import ParentNodeTransformer
import ast


def main():
    with open("src.py", "r", encoding="utf-8") as f:
        code = f.read()

    o = Obfuscator(code)
    with open("dst.py", "w", encoding="utf-8") as f:
        f.write(o.obfuscate())
    print(o.alias_asname)
    print(o.defined_functions)
    print(o.encrypted_constants)
    print(o.encrypt_dict)
    # print(o.convert_to_bin_name("abc"))


if __name__ == "__main__":
    main()
