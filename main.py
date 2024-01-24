from obfuscator import Obfuscator
import ast

# 外側にある関数定義をどうにかする
# 前側に持ってくる
# まず最初に全ノードで関数定義をあさる


def main():
    with open("src.py", "r", encoding="utf-8") as f:
        code = f.read()

    o = Obfuscator(
        code,
        encrypt_variables=True,
        encrypt_consts=True
    )
    with open("dst.py", "w", encoding="utf-8") as f:
        f.write(o.obfuscate())
    # print(o.alias_asname)
    # print(o.defined_functions)
    # print(o.encrypted_constants)
    # print(o.encrypt_dict)
    # print(o.convert_to_bin_name("abc"))


if __name__ == "__main__":
    main()
