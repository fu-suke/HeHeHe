from _ast import Constant, ExceptHandler, Module
import ast
from typing import Any
import random
import math

INTEGER_MASK = 1234567890
FLOAT_MASK = 5432160987
STRING_MASK = 9523045671
BOOLEAN_MASK = 2058934567


class Obfuscator(ast.NodeTransformer):
    def __init__(self, code):
        self.code = code
        self.tree = ast.parse(code)
        self.modules = []
        self.alias_asname = []
        self.defined_functions = []
        self.exceptions = ["self"]  # 例外として変数名を変更しないもの
        self.encrypted_constants = set()  # 暗号化された定数たち
        self.encrypt_dict = {}
        print(ast.dump(self.tree, indent=4))
        print("=====================================")

    def obfuscate(self):
        self.visit(self.tree)
        # print(ast.dump(self.tree, indent=4))
        return ast.unparse(self.tree)

    def visit_Module(self, node: Module) -> Any:
        super().generic_visit(node)
        # 定数を復号する処理を追加
        for k, v in self.encrypt_dict.items():
            n = create_decrypt_function(k, v[0], v[1])
            if not n:
                continue
            node.body.insert(0, n)  # これが失敗する模様
        return node

    def visit_Call(self, node: ast.Call) -> Any:
        # 通常の関数呼び出し（Atrribute呼び出しは除く）
        if isinstance(node.func, ast.Name):
            # def で定義された関数の場合は変数名を変更する
            if node.func.id in self.defined_functions:
                node.func.id = self.encrypt_strings(node.func.id)
            #  import でインポートされた、エイリアスのある関数名の場合は名前を変更する
            if node.func.id in self.alias_asname:
                node.func.id = self.encrypt_strings(node.func.id)

            # 引数の変数名を変更する処理
            args = node.args
            for i, arg in enumerate(args):
                if isinstance(arg, ast.Name):
                    arg.id = self.encrypt_strings(arg.id)
                elif isinstance(arg, ast.Call):
                    self.visit_Call(arg)
                elif isinstance(arg, ast.Constant):
                    args[i] = self.visit_Constant(arg)
                elif isinstance(arg, ast.Attribute):
                    self.visit_Attribute(arg)
                elif isinstance(arg, ast.JoinedStr):
                    for j, v in enumerate(arg.values):
                        self.generic_visit(v)
                else:
                    self.generic_visit(arg)
            return node

        # Attribute呼び出しの場合
        return self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> Any:
        # node.id = node.id[::-1]
        node.id = self.encrypt_strings(node.id)

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.defined_functions.append(node.name)
        node.name = self.encrypt_strings(node.name)
        for arg in node.args.args:
            arg.arg = self.encrypt_strings(arg.arg)
        for b in node.body:
            self.generic_visit(b)
        return node

    def visit_Import(self, node: ast.Import) -> Any:
        for alias in node.names:
            self.modules.append(alias.name)
            if alias.asname:
                self.alias_asname.append(alias.asname)
                alias.asname = self.encrypt_strings(alias.asname)
        self.generic_visit(node)
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        # self.modules.append(node.module)
        for alias in node.names:
            if alias.asname:
                self.alias_asname.append(alias.asname)
                alias.asname = self.encrypt_strings(alias.asname)
        self.generic_visit(node)
        return node

    def visit_ExceptHandler(self, node: ExceptHandler) -> Any:
        for b in node.body:
            self.generic_visit(b)
        return node

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        if isinstance(node.value, ast.Name):
            # self.~~ の場合は~~を変更する
            if node.value.id == "self":
                node.attr = self.encrypt_strings(node.attr)
            # 宣言された関数名に含まれている場合は関数名を変更する
            # a.method() の場合は method が defiend_functions に含まれているかを確認する
            elif node.attr in self.defined_functions:
                node.attr = self.encrypt_strings(node.attr)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.defined_functions.append(node.name)
        node.name = self.encrypt_strings(node.name)
        self.generic_visit(node)
        return node

    def visit_Constant(self, node: ast.Constant) -> Any:
        # print("visit_Constant: ", node.value, type(node.value))
        encrypted_constant = self.encrypt_const(node.value)
        node = ast.Call(func=ast.Name(id=encrypted_constant, ctx=ast.Load()),
                        args=[], keywords=[])
        return node

    def encrypt_strings(self, name: str) -> str:
        assert isinstance(name, str)
        if name in self.modules:
            return name
        if name in self.exceptions:
            return name
        if name.startswith("__"):
            return name

        name = name.encode()
        new_name = ""
        for hex in name:
            # 2進数に変換
            binary = bin(hex)
            for b in binary:
                if b == "b":
                    continue
                new_name += ("M" if b == "0" else "W")
        return "" + new_name

    def encrypt_const(self, value) -> Any:
        import struct
        self.encrypted_constants.add(value)
        const_type = type(value)
        if const_type == str:
            pass
        elif const_type == int:
            value = value ^ INTEGER_MASK
        elif const_type == float:
            # 浮動小数点数をビット表現に変換し、整数として解釈
            value = struct.unpack('!I', struct.pack('!f', value))[
                0] ^ FLOAT_MASK
        elif const_type == bool:
            value = value ^ BOOLEAN_MASK
        else:
            raise ValueError(f"Unknown type: {type(value)}")

        new_name = convert_to_bin_name(value)
        if value not in self.encrypt_dict:
            self.encrypt_dict[new_name] = [value, const_type]
        return new_name


def create_decrypt_function(encrypted_value, original_value, const_type):
    n = ast.FunctionDef(name=encrypted_value, args=ast.arguments(
        posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]), body=[], decorator_list=[])
    n.lineno = 3
    n.col_offset = 0

    if const_type == str:
        n.body.append(
            ast.parse(generate_code_for_string(original_value)).body[0])
        return n
    elif const_type == int:
        n.body.append(
            ast.parse(generate_code_for_integer(original_value)).body[0])
        return n
    elif const_type == float:
        n.body.append(
            ast.parse(generate_code_for_float(original_value)).body[:2])
        return n
    elif const_type == bool:
        n.body.append(
            ast.parse(generate_code_for_integer(original_value)).body[0])
        return n
    # if const_type == str:
    #     n.body.append(ast.parse(
    #         f"bin_str = {encrypted_value}\nbinary_str = ''.join('0' if char == 'へ' else '1' for char in bin_str)\nreturn int(binary_str, 2).to_bytes((len(binary_str) + 7) // 8, byteorder='big')").body[0:3])
    # elif const_type == int:
    #     n.body.append(ast.parse("return 'integer'").body[0])
    # elif const_type == float:
    #     n.body.append(ast.parse("return 'float'").body[0])
    # elif const_type == bool:
    #     n.body.append(ast.parse("return 'boolean'").body[0])
    # else:
    #     raise ValueError(f"Unknown type: {type(const_type)}")
    # return n


def convert_to_bin_name(data):
    assert (isinstance(data, int) or isinstance(data, str))
    if isinstance(data, str):
        data = data.encode()
        binary = ""
        for hex in data:
            binary += bin(hex)[2:]
    else:
        binary = bin(data)
    new_name = ""
    for b in binary:
        if b == "b":
            continue
        new_name += ("ぽ" if b == "0" else "ヘ")
    return new_name


def generate_code_for_string(input_str):
    program_parts = []
    for char in input_str:
        char_code = ord(char)
        # ここで文字コードを隠蔽するための計算を行う
        # 例: char_codeを2で割った値に2を足して再び2を掛ける（元の値に戻る）
        masked_code = f"(int({char_code} / 2 * 2))"
        program_parts.append(f"chr({masked_code})")

    # 文字列を連結して完全なプログラムを作成
    program = " + ".join(program_parts)
    return "return " + program


def generate_code_for_integer(num):
    # 複数のランダムな大きな数を生成
    num1 = random.randint(100000, 999999)
    num2 = random.randint(100000, 999999)
    num3 = random.randint(100000, 999999)

    # 複雑な計算を行う
    step1 = num ^ num1
    step2 = step1 + num2
    step3 = step2 - num3

    # 元の数に戻すための計算を行うコードを生成
    program = f"(({step3} + {num3} - {num2}) ^ {num1})"
    return "return " + program


def generate_code_for_float(num):
    # 浮動小数点数の仮数部と指数部を取得
    mantissa, exponent = math.frexp(num)
    exponent = exponent - 1  # 調整

    # 2の累乗の数をランダムに生成
    power_of_two = 2 ** random.randint(20, 30)

    # 仮数部と指数部に対する計算を生成
    mantissa_calc = f"({mantissa} * {power_of_two}) / {power_of_two}"
    exponent_calc = f"({exponent} + 1)"

    # 元の浮動小数点数を再構築するコードを生成
    program = f"import math\nreturn math.ldexp({mantissa_calc}, {exponent_calc})"
    return program
