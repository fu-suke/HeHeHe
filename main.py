from obfuscator import Obfuscator
import ast


def main():
    with open("src.py", "r", encoding="utf-8") as f:
        code = f.read()

    o = Obfuscator(
        code,
        encrypt_variables=True,
        encrypt_consts=True,
        encrypt_builtins=True,
    )
    with open("dst.py", "w", encoding="utf-8") as f:
        f.write(o.obfuscate())


if __name__ == "__main__":
    main()
