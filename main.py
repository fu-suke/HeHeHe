from obfuscator import Obfuscator


def main():
    with open("src.py", "r", encoding="utf-8") as f:
        code = f.read()

    o = Obfuscator(
        code,
        # encrypt_idents=False,
        # encrypt_consts=False,
        encrypt_builtins=True,
        zero="へ",
        one="ヘ",
        prefix="",
    )
    with open("dst.py", "w", encoding="utf-8") as f:
        f.write(o.obfuscate())


if __name__ == "__main__":
    main()