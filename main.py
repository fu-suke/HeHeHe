from obfuscator import Obfuscator
import argparse


def main(input_file, output_file, encrypt_idents, encrypt_consts, encrypt_builtins, zero, one, prefix):
    with open(input_file, "r", encoding="utf-8") as f:
        code = f.read()

    o = Obfuscator(
        code,
        encrypt_idents=encrypt_idents,
        encrypt_consts=encrypt_consts,
        encrypt_builtins=encrypt_builtins,
        zero=zero,
        one=one,
        prefix=prefix,
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(o.obfuscate())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="コードの難読化ツール")
    parser.add_argument("input_file", help="難読化するソースコードのファイルパス")
    parser.add_argument("output_file", help="難読化されたコードを保存するファイルパス")
    parser.add_argument("--encrypt_idents", action='store_true',
                        default=True, help="識別子の難読化を有効にする（デフォルト：ON）")
    parser.add_argument("--encrypt_consts", action='store_true',
                        default=True, help="定数の難読化を有効にする（デフォルト：ON）")
    parser.add_argument("--encrypt_builtins", action='store_true',
                        default=False, help="組み込み関数の難読化を有効にする（デフォルト：OFF）")
    parser.add_argument("--zero", default="へ", help="難読化に使用する '0' の代替文字")
    parser.add_argument("--one", default="ヘ", help="難読化に使用する '1' の代替文字")
    parser.add_argument("--prefix", default="", help="識別子に付加するプレフィックス")

    args = parser.parse_args()

    main(args.input_file, args.output_file, args.encrypt_idents,
         args.encrypt_consts, args.encrypt_builtins, args.zero, args.one, args.prefix)
