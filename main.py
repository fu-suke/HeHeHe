from obfuscator import Obfuscator
import ast


def main():
    with open("src.py", "r", encoding="utf-8") as f:
        code = f.read()

    # tf = [True, False]
    # for encrypt_idents in tf:
    #     for encrypt_consts in tf:
    #         for encrypt_builtins in tf:
    #             o = Obfuscator(
    #                 code,
    #                 encrypt_idents=encrypt_idents,
    #                 encrypt_consts=encrypt_consts,
    #                 encrypt_builtins=encrypt_builtins,
    #             )
    #             with open("dst.py", "w", encoding="utf-8") as f:
    #                 obfuscated_code = o.obfuscate()
    #                 f.write(obfuscated_code)

    o = Obfuscator(
        code,
        # encrypt_idents=False,
        # encrypt_consts=False,
        encrypt_builtins=True,
        zero="0",
        one="O",
        prefix="O",
    )
    with open("dst.py", "w", encoding="utf-8") as f:
        f.write(o.obfuscate())


if __name__ == "__main__":
    main()

# str, int, bool, float, None, bytes, ...
