from obfuscator import Obfuscator


def main():
    with open("src.py", "r") as f:
        code = f.read()

    o = Obfuscator(code)
    with open("dst.py", "w") as f:
        f.write(o.obfuscate())
    print(o.alias_asname)
    print(o.defined_functions)


if __name__ == "__main__":
    main()
