from obfuscator import Obfuscator
import argparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() == 'true':
        return True
    elif v.lower() == 'false':
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


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
    parser = argparse.ArgumentParser(description="HeHeHe Obfuscator")
    parser.add_argument(
        "input_file", help="File path to the Python code to obfuscate")
    parser.add_argument(
        "-o", "--output-file", default="out.py", help="Output file path (default: out.py)")
    parser.add_argument("-i", "--encrypt-idents", type=str2bool, choices=[True, False], default=True,
                        help="Enables identifier obfuscation (default: ON)")
    parser.add_argument("-c", "--encrypt-consts", type=str2bool, choices=[True, False], default=True,
                        help="Enables constant obfuscation (default: ON)")
    parser.add_argument("-b", "--encrypt-builtins", type=str2bool, choices=[True, False], default=False,
                        help="Enables obfuscation of built-in functions and classes (default: OFF)")
    parser.add_argument("--zero", default="へ",
                        help="Obfuscation character for '0'")
    parser.add_argument("--one", default="ヘ",
                        help="Obfuscation character for '1'")
    parser.add_argument("--prefix", default="",
                        help="Prefix for obfuscated identifiers")

    args = parser.parse_args()

    main(args.input_file, args.output_file, args.encrypt_idents,
         args.encrypt_consts, args.encrypt_builtins, args.zero, args.one, args.prefix)

    print("Obfuscation completed!:", args.input_file, "->", args.output_file)
